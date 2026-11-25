# English Reminder

A lightweight Windows desktop English phrase reminder.

## Features

- SQLite local database
- Import phrases/examples from TXT
- Topic-based random reminders
- Custom popup at the bottom-right of the screen
- Local MP3 generation with `edge-tts`
- Audio is generated once and reused
- Windows startup option
- System tray
- Phrase manager
- Settings

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## TXT format

```text
[At Home]

Stand up. | /stænd ʌp/ | Đứng lên.
  > Please stand up. | /pliːz stænd ʌp/ | Hãy đứng lên nhé.
  > Can you stand up? | /kæn juː stænd ʌp/ | Con có thể đứng lên không?

Sit down. | /sɪt daʊn/ | Ngồi xuống.
  > Please sit down. | /pliːz sɪt daʊn/ | Hãy ngồi xuống nhé.
```

A line without `>` creates an expression.
A line starting with `>` creates an example sentence for the previous expression.

## Notes

`edge-tts` requires network access when generating new audio.
After MP3 files are generated, playback is local.
