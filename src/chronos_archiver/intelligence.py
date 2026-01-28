"""Intelligence module - Content analysis and extraction engine."""

import logging
import re
from typing import Any, Optional
from urllib.parse import urlparse

import spacy
from langdetect import detect_langs

from chronos_archiver.models import ContentAnalysis, MediaEmbed, TransformedContent

logger = logging.getLogger(__name__)


class IntelligenceEngine:
    """Motor de inteligência para análise de conteúdo arquivado.
    
    Intelligence engine for analyzing archived content, extracting:
    - Language detection
    - Named entities (people, organizations, locations)
    - Keywords and topics
    - Media embeds (YouTube, Vimeo, etc.)
    - Sentiment analysis
    - Content classification
    """

    def __init__(self, config: Optional[dict] = None) -> None:
        """Initialize intelligence engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        intel_config = self.config.get("intelligence", {})
        
        self.enable_nlp = intel_config.get("enable_nlp", True)
        self.enable_entity_extraction = intel_config.get("enable_entity_extraction", True)
        self.enable_language_detection = intel_config.get("enable_language_detection", True)
        self.enable_embed_detection = intel_config.get("enable_embed_detection", True)
        
        # Load spaCy model for Portuguese and multilingual
        self.nlp_pt = None
        self.nlp_multi = None
        
        if self.enable_nlp:
            try:
                self.nlp_pt = spacy.load("pt_core_news_sm")
                logger.info("Loaded Portuguese NLP model")
            except OSError:
                logger.warning("Portuguese spaCy model not found. Install with: python -m spacy download pt_core_news_sm")
            
            try:
                self.nlp_multi = spacy.load("xx_ent_wiki_sm")
                logger.info("Loaded multilingual NLP model")
            except OSError:
                logger.warning("Multilingual spaCy model not found. Install with: python -m spacy download xx_ent_wiki_sm")

    async def analyze(self, transformed: TransformedContent) -> ContentAnalysis:
        """Analyze transformed content for intelligence extraction.
        
        Args:
            transformed: Transformed content to analyze
            
        Returns:
            ContentAnalysis with extracted intelligence
        """
        logger.info(f"Analyzing content: {transformed.snapshot.url}")
        
        analysis = ContentAnalysis(
            snapshot=transformed.snapshot,
            text_content=transformed.text_content or "",
        )
        
        # Language detection
        if self.enable_language_detection:
            analysis.languages = self._detect_languages(transformed.text_content)
        
        # Extract embeds (YouTube, Vimeo, etc.)
        if self.enable_embed_detection:
            analysis.media_embeds = self._extract_embeds(transformed.content)
        
        # NLP analysis
        if self.enable_nlp and transformed.text_content:
            # Choose appropriate model
            primary_lang = analysis.languages[0][0] if analysis.languages else "pt"
            nlp = self.nlp_pt if primary_lang == "pt" else self.nlp_multi
            
            if nlp:
                # Named entity extraction
                if self.enable_entity_extraction:
                    analysis.entities = self._extract_entities(transformed.text_content, nlp)
                
                # Keyword extraction
                analysis.keywords = self._extract_keywords(transformed.text_content, nlp)
                
                # Topic classification
                analysis.topics = self._classify_topics(transformed.text_content, nlp)
        
        # Extract additional metadata
        analysis.word_count = len(transformed.text_content.split()) if transformed.text_content else 0
        analysis.has_images = "<img" in transformed.content.lower()
        analysis.has_videos = bool(analysis.media_embeds)
        
        logger.info(f"Analysis complete: {len(analysis.entities)} entities, {len(analysis.media_embeds)} embeds")
        
        return analysis

    def _detect_languages(self, text: Optional[str]) -> list[tuple[str, float]]:
        """Detect languages in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of (language_code, probability) tuples
        """
        if not text or len(text.strip()) < 10:
            return []
        
        try:
            langs = detect_langs(text[:1000])  # Analyze first 1000 chars
            return [(lang.lang, lang.prob) for lang in langs]
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return []

    def _extract_embeds(self, html: str) -> list[MediaEmbed]:
        """Extract media embeds from HTML.
        
        Detects:
        - YouTube embeds
        - Vimeo embeds
        - Dailymotion embeds
        - SoundCloud embeds
        - Generic iframes
        
        Args:
            html: HTML content
            
        Returns:
            List of MediaEmbed objects
        """
        embeds = []
        
        # YouTube patterns
        youtube_patterns = [
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in youtube_patterns:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                video_id = match.group(1)
                embeds.append(MediaEmbed(
                    type="youtube",
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    embed_url=f"https://www.youtube.com/embed/{video_id}",
                    video_id=video_id,
                    platform="YouTube",
                ))
        
        # Vimeo patterns
        vimeo_patterns = [
            r'vimeo\.com/video/([0-9]+)',
            r'vimeo\.com/([0-9]+)',
            r'player\.vimeo\.com/video/([0-9]+)',
        ]
        
        for pattern in vimeo_patterns:
            for match in re.finditer(pattern, html, re.IGNORECASE):
                video_id = match.group(1)
                embeds.append(MediaEmbed(
                    type="vimeo",
                    url=f"https://vimeo.com/{video_id}",
                    embed_url=f"https://player.vimeo.com/video/{video_id}",
                    video_id=video_id,
                    platform="Vimeo",
                ))
        
        # Dailymotion
        dailymotion_pattern = r'dailymotion\.com/(?:video|embed)/([a-zA-Z0-9]+)'
        for match in re.finditer(dailymotion_pattern, html, re.IGNORECASE):
            video_id = match.group(1)
            embeds.append(MediaEmbed(
                type="dailymotion",
                url=f"https://www.dailymotion.com/video/{video_id}",
                embed_url=f"https://www.dailymotion.com/embed/video/{video_id}",
                video_id=video_id,
                platform="Dailymotion",
            ))
        
        # SoundCloud
        soundcloud_pattern = r'soundcloud\.com/([^"\s]+)'
        for match in re.finditer(soundcloud_pattern, html, re.IGNORECASE):
            track_url = f"https://soundcloud.com/{match.group(1)}"
            embeds.append(MediaEmbed(
                type="soundcloud",
                url=track_url,
                embed_url=track_url,
                platform="SoundCloud",
            ))
        
        # Generic iframe detection
        iframe_pattern = r'<iframe[^>]+src=["\']([^"\'>]+)["\']'
        for match in re.finditer(iframe_pattern, html, re.IGNORECASE):
            iframe_src = match.group(1)
            # Skip if already detected
            if any(embed.embed_url == iframe_src for embed in embeds):
                continue
            
            parsed = urlparse(iframe_src)
            embeds.append(MediaEmbed(
                type="iframe",
                url=iframe_src,
                embed_url=iframe_src,
                platform=parsed.netloc,
            ))
        
        logger.info(f"Found {len(embeds)} media embeds")
        return embeds

    def _extract_entities(self, text: str, nlp) -> dict[str, list[str]]:
        """Extract named entities from text.
        
        Args:
            text: Text to analyze
            nlp: spaCy NLP model
            
        Returns:
            Dictionary of entity types to entity lists
        """
        doc = nlp(text[:100000])  # Limit to 100k chars
        
        entities = {
            "PERSON": [],      # Pessoas
            "ORG": [],         # Organizações
            "LOC": [],         # Locais
            "DATE": [],        # Datas
            "EVENT": [],       # Eventos
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entity_text = ent.text.strip()
                if entity_text and entity_text not in entities[ent.label_]:
                    entities[ent.label_].append(entity_text)
        
        return entities

    def _extract_keywords(self, text: str, nlp, max_keywords: int = 20) -> list[str]:
        """Extract keywords from text using noun phrases.
        
        Args:
            text: Text to analyze
            nlp: spaCy NLP model
            max_keywords: Maximum keywords to extract
            
        Returns:
            List of keywords
        """
        doc = nlp(text[:50000])
        
        # Extract noun chunks and their frequency
        keyword_freq = {}
        for chunk in doc.noun_chunks:
            keyword = chunk.text.lower().strip()
            if len(keyword) > 2 and len(keyword.split()) <= 3:
                keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in sorted_keywords[:max_keywords]]

    def _classify_topics(self, text: str, nlp) -> list[str]:
        """Classify content into topics.
        
        Args:
            text: Text to analyze
            nlp: spaCy NLP model
            
        Returns:
            List of topic labels
        """
        topics = []
        
        # Simple keyword-based topic classification
        # Can be enhanced with ML models
        
        topic_keywords = {
            "religião": ["igreja", "diocese", "bispo", "paróquia", "anglicana", "episcopal", "fé", "culto"],
            "notícias": ["notícia", "anúncio", "comunicado", "informação", "evento"],
            "história": ["história", "histórico", "origem", "fundação", "tradição"],
            "comunidade": ["comunidade", "paroquianos", "membros", "família", "grupo"],
            "educação": ["educação", "ensino", "formação", "curso", "treinamento"],
            "social": ["social", "ação", "projeto", "ajuda", "assistência"],
        }
        
        text_lower = text.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary of the text.
        
        Args:
            text: Text to summarize
            max_sentences: Maximum sentences in summary
            
        Returns:
            Summary text
        """
        if not text:
            return ""
        
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Return first N sentences as summary
        summary_sentences = sentences[:max_sentences]
        return ". ".join(summary_sentences) + "." if summary_sentences else ""