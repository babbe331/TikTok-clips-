import os
import time
import subprocess
import glob

# ── Configuration ─────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = "sk_30433aabbb78ffe273fa642f738cdc9547af7d2c28709f60"
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
GOOGLE_API_KEY = "AQ.Ab8RN6K5TsT5T_a5ww-PeNkA8FaCpCljA_G4iDl7YaAjy5KdbQ"

# ── Story scenes ───────────────────────────────────────────────────────────────
scenes = [
    {
        "text": "They told you the deep ocean was empty. They lied.",
        "prompt": "Cinematic dark moody shot, deep underwater abyss, photorealistic horror, 9:16 aspect ratio",
    },
    {
        "text": "In 1997, scientists recorded a sound louder than a blue whale.",
        "prompt": "Submarine sonar screen glowing green in pitch black ocean water, retro tech, horror atmosphere, 9:16 aspect ratio",
    },
    {
        "text": "The military classified it immediately. They called it The Bloop.",
        "prompt": "Classified government stamp on a manila folder, red TOP SECRET text, dark moody office, 9:16 aspect ratio",
    },
    {
        "text": "The military claimed it was just ice shifting. But the data says otherwise.",
        "prompt": "Classified military documents on a dark wooden table, old folder, dramatic overhead lighting, 9:16 aspect ratio",
    },
    {
        "text": "The coordinates pointed to a trench that sat silent for thirty years.",
        "prompt": "Deep oceanic trench mapping software on an old CRT monitor, glitch effect, eerie, 9:16 aspect ratio",
    },
    {
        "text": "Until last night, when the sound started repeating. What is waking up?",
        "prompt": "Massive glowing eyes waking up in the deep dark ocean abyss, terrifying cinematic shot, 9:16 aspect ratio",
    },
    {
        "text": "A research vessel was sent to the trench. It never came back.",
        "prompt": "Abandoned research ship drifting in dark fog covered ocean at night, horror cinematic, 9:16 aspect ratio",
    },
    {
        "text": "The last transmission was a single image. Something was looking back at them.",
        "prompt": "Grainy underwater camera footage showing a massive dark shape rising from below, horror, 9:16 aspect ratio",
    },
    {
        "text": "Scientists estimate the creature is larger than a city. Older than humanity.",
        "prompt": "Enormous ancient sea creature silhouette dwarfing skyscrapers underwater, scale horror, cinematic, 9:16 aspect ratio",
    },
    {
        "text": "It has been down there since before the dinosaurs. Sleeping. Waiting.",
        "prompt": "Ancient deep sea creature dormant on ocean floor covered in barnacles and sediment, cosmic horror, 9:16 aspect ratio",
    },
    {
        "text": "Three governments have gone dark on all ocean monitoring systems.",
        "prompt": "World map with multiple locations going dark one by one, news alert screen, eerie blue glow, 9:16 aspect ratio",
    },
    {
        "text": "Coastal cities are being quietly evacuated. No official reason given.",
        "prompt": "People quietly evacuating a coastal city at night, military trucks, no panic but eerie silence, 9:16 aspect ratio",
    },
    {
        "text": "The ocean floor is rising. Something enormous is pushing up from below.",
        "prompt": "Ocean surface bulging and rising from below, massive underwater displacement wave, horror, 9:16 aspect ratio",
    },
    {
        "text": "They knew this day would come. They just never told us.",
        "prompt": "Government officials in a dark bunker watching screens showing ocean disturbance, tense atmosphere, 9:16 aspect ratio",
    },
    {
        "text": "The sound has a rhythm now. Like breathing. It is almost here.",
        "prompt": "Sonar display showing rhythmic pulse getting closer and closer to surface, horror tech, 9:16 aspect ratio",
    },
]


# ── Step A: ElevenLabs Voiceover ───────────────────────────────────────────────
def generate_voiceover():
    print("\n[A] Generating voiceover with ElevenLabs...")
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    narration = " ".join(s["text"] for s in scenes)
    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    audio = client.text_to_speech.convert(
        voice_id=ELEVENLABS_VOICE_ID,
        text=narration,
        model_id="eleven_monolingual_v1",
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75),
    )

    with open("voiceover.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)

    print("    Saved voiceover.mp3")


# ── Step B: Subtitle timestamps via Whisper ────────────────────────────────────
def generate_subtitles():
    print("\n[B] Transcribing voiceover with Whisper...")
    import whisper

    model = whisper.load_model("base")
    result = model.transcribe("voiceover.mp3", word_timestamps=True)

    words = []
    for segment in result["segments"]:
        for w in segment.get("words", []):
            words.append(
                {
                    "word": w["word"].strip().upper(),
                    "start": w["start"],
                    "end": w["end"],
                }
            )

    # Group into chunks of 2–4 words
    chunk_size = 3
    chunks = [words[i : i + chunk_size] for i in range(0, len(words), chunk_size)]

    def fmt_time(t):
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for idx, chunk in enumerate(chunks, start=1):
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        text = " ".join(w["word"] for w in chunk)
        lines.append(f"{idx}")
        lines.append(f"{fmt_time(start)} --> {fmt_time(end)}")
        lines.append(text)
        lines.append("")

    with open("subtitles.srt", "w") as f:
        f.write("\n".join(lines))

    print(f"    Wrote {len(chunks)} subtitle entries to subtitles.srt")


# ── Step C: Google Veo 2 video generation ─────────────────────────────────────
def generate_videos():
    print("\n[C] Generating video clips with Google Veo 2...")
    from google import genai

    client = genai.Client(api_key=GOOGLE_API_KEY)

    for i, scene in enumerate(scenes):
        clip_path = f"clip{i}.mp4"
        print(f"    Scene {i}: {scene['prompt'][:60]}...")

        attempt = 0
        operation = None

        while attempt < 3:
            try:
                operation = client.models.generate_videos(
                    model="veo-2.0-generate-001",
                    prompt=scene["prompt"],
                    config={"aspect_ratio": "9:16"},
                )
                break
            except Exception as e:
                if "429" in str(e) or "quota" in str(e).lower():
                    print(f"    429 rate limit hit — waiting 60s before retry...")
                    time.sleep(60)
                    attempt += 1
                else:
                    raise

        if operation is None:
            print(f"    WARNING: Failed to start generation for scene {i}, skipping.")
            continue

        # Poll until done
        print(f"    Polling operation for scene {i}...")
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)

        video = operation.result.generated_videos[0]
        video_bytes = client.files.download(file=video.video)
        with open(clip_path, "wb") as f:
            f.write(video_bytes)
        print(f"    Saved {clip_path}")

        # Respect free-tier rate limits between scenes
        if i < len(scenes) - 1:
            print("    Waiting 30s before next scene request...")
            time.sleep(30)


# ── Step D: FFmpeg assembly ────────────────────────────────────────────────────
def assemble_video():
    print("\n[D] Assembling final video with FFmpeg...")

    clip_files = sorted(glob.glob("clip*.mp4"))
    if not clip_files:
        raise RuntimeError("No clip files found — video generation may have failed.")

    with open("concat.txt", "w") as f:
        for clip in clip_files:
            f.write(f"file '{clip}'\n")

    subtitle_style = (
        "FontName=Arial,"
        "FontSize=18,"
        "PrimaryColour=&H00FFFF00,"  # yellow
        "OutlineColour=&H00000000,"  # black
        "BorderStyle=1,"
        "Outline=3,"
        "Alignment=2"                # bottom-center
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "concat.txt",
        "-i", "voiceover.mp3",
        "-vf", f"subtitles=subtitles.srt:force_style='{subtitle_style}'",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "google_veo_horror_full.mp4",
    ]

    print("    Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("    FFmpeg stderr:\n", result.stderr)
        raise RuntimeError("FFmpeg failed — see stderr above.")

    print("    Saved google_veo_horror.mp4")


# ── Step E: Cleanup ────────────────────────────────────────────────────────────
def cleanup():
    print("\n[E] Cleaning up temporary files...")
    for pattern in ("clip*.mp4", "concat.txt", "voiceover.mp3", "subtitles.srt"):
        for path in glob.glob(pattern):
            os.remove(path)
            print(f"    Deleted {path}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        generate_voiceover()
        generate_subtitles()
        generate_videos()
        assemble_video()
        cleanup()
        print("\nDone! Final video: google_veo_horror.mp4")
    except Exception as e:
        print(f"\nPipeline error: {e}")
        raise
