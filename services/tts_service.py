import asyncio
from pathlib import Path
import edge_tts


class TTSService:
    def __init__(self, audio_dir="data/audio", voice="en-US-JennyNeural", rate="+0%"):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.voice = voice
        self.rate = rate

    async def _generate(self, text, output_path):
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate
        )
        await communicate.save(str(output_path))

    def generate(self, text, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        asyncio.run(self._generate(text, output_path))
        return str(output_path)

    def generate_for_id(self, text, item_id):
        path = self.audio_dir / f"{item_id}.mp3"
        if not path.exists():
            self.generate(text, path)
        return str(path)
