"""Tests for intelligence engine."""

import pytest
from chronos_archiver.intelligence import IntelligenceEngine
from chronos_archiver.models import ContentAnalysis


class TestIntelligenceEngine:
    """Test IntelligenceEngine class."""

    @pytest.mark.asyncio
    async def test_analyze_content(self, test_config, sample_transformed_content):
        """Test content analysis."""
        engine = IntelligenceEngine(test_config)
        
        analysis = await engine.analyze(sample_transformed_content)
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.snapshot == sample_transformed_content.snapshot
        assert analysis.text_content is not None

    @pytest.mark.asyncio
    async def test_language_detection(self, test_config, sample_transformed_content):
        """Test language detection."""
        engine = IntelligenceEngine(test_config)
        
        # Add Portuguese text
        sample_transformed_content.text_content = "Esta é uma página em português sobre a Diocese Anglicana do Recife."
        
        analysis = await engine.analyze(sample_transformed_content)
        
        assert len(analysis.languages) > 0
        # Should detect Portuguese
        assert any(lang == "pt" for lang, _ in analysis.languages)

    @pytest.mark.asyncio
    async def test_embed_detection_youtube(self, test_config, sample_snapshot):
        """Test YouTube embed detection."""
        from chronos_archiver.models import TransformedContent
        
        engine = IntelligenceEngine(test_config)
        
        html_with_youtube = '''
        <html>
        <body>
            <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" width="560" height="315"></iframe>
            <a href="https://www.youtube.com/watch?v=abc123">Video</a>
        </body>
        </html>
        '''
        
        transformed = TransformedContent(
            snapshot=sample_snapshot,
            content=html_with_youtube,
            text_content="Test content",
        )
        
        analysis = await engine.analyze(transformed)
        
        # Should find YouTube embeds
        youtube_embeds = [e for e in analysis.media_embeds if e.type == "youtube"]
        assert len(youtube_embeds) >= 1
        assert any("dQw4w9WgXcQ" in e.video_id for e in youtube_embeds if e.video_id)

    @pytest.mark.asyncio
    async def test_embed_detection_vimeo(self, test_config, sample_snapshot):
        """Test Vimeo embed detection."""
        from chronos_archiver.models import TransformedContent
        
        engine = IntelligenceEngine(test_config)
        
        html_with_vimeo = '''
        <html>
        <body>
            <iframe src="https://player.vimeo.com/video/123456789" width="640" height="360"></iframe>
        </body>
        </html>
        '''
        
        transformed = TransformedContent(
            snapshot=sample_snapshot,
            content=html_with_vimeo,
            text_content="Test content",
        )
        
        analysis = await engine.analyze(transformed)
        
        # Should find Vimeo embeds
        vimeo_embeds = [e for e in analysis.media_embeds if e.type == "vimeo"]
        assert len(vimeo_embeds) >= 1
        assert any("123456789" in e.video_id for e in vimeo_embeds if e.video_id)

    @pytest.mark.asyncio
    async def test_keyword_extraction(self, test_config, sample_transformed_content):
        """Test keyword extraction."""
        # Skip if NLP models not available
        engine = IntelligenceEngine(test_config)
        
        if not engine.nlp_pt:
            pytest.skip("Portuguese NLP model not available")
        
        sample_transformed_content.text_content = """
        A Diocese Anglicana do Recife é uma instituição religiosa importante.
        A igreja episcopal serve a comunidade local com dedicação.
        O bispo lidera as paróquias da região.
        """
        
        analysis = await engine.analyze(sample_transformed_content)
        
        assert len(analysis.keywords) > 0
        # Should extract relevant keywords
        assert any("diocese" in kw.lower() for kw in analysis.keywords)

    @pytest.mark.asyncio
    async def test_topic_classification(self, test_config, sample_transformed_content):
        """Test topic classification."""
        engine = IntelligenceEngine(test_config)
        
        sample_transformed_content.text_content = """
        A igreja realiza cultos todos os domingos. A diocese organiza eventos
        religiosos para a comunidade. O bispo visitou várias paróquias.
        """
        
        analysis = await engine.analyze(sample_transformed_content)
        
        assert len(analysis.topics) > 0
        # Should classify as religious content
        assert "religião" in analysis.topics or "comunidade" in analysis.topics

    @pytest.mark.asyncio
    async def test_summary_generation(self, test_config):
        """Test summary generation."""
        engine = IntelligenceEngine(test_config)
        
        text = """
        Esta é a primeira frase. Esta é a segunda frase muito importante.
        Esta é a terceira frase. Esta é a quarta frase que não deve aparecer.
        """
        
        summary = engine.generate_summary(text, max_sentences=2)
        
        assert "primeira frase" in summary
        assert "segunda frase" in summary
        assert "quarta frase" not in summary