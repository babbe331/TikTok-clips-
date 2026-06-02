import os
import time
import subprocess
import glob

# ── Configuration ─────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = "PASTE_YOUR_ELEVENLABS_KEY_HERE"
ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
GOOGLE_API_KEY = "PASTE_YOUR_GOOGLE_KEY_HERE"

# ── Story scenes ───────────────────────────────────────────────────────────────
PARTS = [
    # ── Part 1: The Awakening ──────────────────────────────────────────────────
    {
        "output": "part1_awakening.mp4",
        "scenes": [
            {"text": "They told you the deep ocean was empty. They lied.", "prompt": "Cinematic dark moody shot, deep underwater abyss, photorealistic horror, 9:16 aspect ratio"},
            {"text": "In 1997, scientists recorded a sound louder than a blue whale.", "prompt": "Submarine sonar screen glowing green in pitch black ocean water, retro tech, horror atmosphere, 9:16 aspect ratio"},
            {"text": "The military classified it immediately. They called it The Bloop.", "prompt": "Classified government stamp on a manila folder, red TOP SECRET text, dark moody office, 9:16 aspect ratio"},
            {"text": "The military claimed it was just ice shifting. But the data says otherwise.", "prompt": "Classified military documents on a dark wooden table, old folder, dramatic overhead lighting, 9:16 aspect ratio"},
            {"text": "The coordinates pointed to a trench that sat silent for thirty years.", "prompt": "Deep oceanic trench mapping software on an old CRT monitor, glitch effect, eerie, 9:16 aspect ratio"},
            {"text": "Until last night, when the sound started repeating. What is waking up?", "prompt": "Massive glowing eyes waking up in the deep dark ocean abyss, terrifying cinematic shot, 9:16 aspect ratio"},
            {"text": "A research vessel was sent to the trench. It never came back.", "prompt": "Abandoned research ship drifting in dark fog covered ocean at night, horror cinematic, 9:16 aspect ratio"},
            {"text": "The last transmission was a single image. Something was looking back at them.", "prompt": "Grainy underwater camera footage showing a massive dark shape rising from below, horror, 9:16 aspect ratio"},
            {"text": "Scientists estimate the creature is larger than a city. Older than humanity.", "prompt": "Enormous ancient sea creature silhouette dwarfing skyscrapers underwater, scale horror, cinematic, 9:16 aspect ratio"},
            {"text": "It has been down there since before the dinosaurs. Sleeping. Waiting.", "prompt": "Ancient deep sea creature dormant on ocean floor covered in barnacles and sediment, cosmic horror, 9:16 aspect ratio"},
            {"text": "Three governments have gone dark on all ocean monitoring systems.", "prompt": "World map with multiple locations going dark one by one, news alert screen, eerie blue glow, 9:16 aspect ratio"},
            {"text": "Coastal cities are being quietly evacuated. No official reason given.", "prompt": "People quietly evacuating a coastal city at night, military trucks, no panic but eerie silence, 9:16 aspect ratio"},
            {"text": "The ocean floor is rising. Something enormous is pushing up from below.", "prompt": "Ocean surface bulging and rising from below, massive underwater displacement wave, horror, 9:16 aspect ratio"},
            {"text": "They knew this day would come. They just never told us.", "prompt": "Government officials in a dark bunker watching screens showing ocean disturbance, tense atmosphere, 9:16 aspect ratio"},
            {"text": "The sound has a rhythm now. Like breathing. It is almost here.", "prompt": "Sonar display showing rhythmic pulse getting closer and closer to surface, horror tech, 9:16 aspect ratio"},
        ],
    },
    # ── Part 2: The Surface ────────────────────────────────────────────────────
    {
        "output": "part2_surface.mp4",
        "scenes": [
            {"text": "At 3:47 AM, it breached the surface for the first time in sixty million years.", "prompt": "Colossal ancient creature breaking the ocean surface at night, massive water displacement, cinematic horror, 9:16 aspect ratio"},
            {"text": "The shockwave alone leveled buildings across five coastal cities.", "prompt": "City buildings crumbling from a massive shockwave at night, cinematic disaster, 9:16 aspect ratio"},
            {"text": "Every ocean sensor on Earth went offline simultaneously.", "prompt": "Global map of sensor networks going dark all at once, eerie tech horror, 9:16 aspect ratio"},
            {"text": "Pilots reported seeing it from thirty thousand feet. They refused to land.", "prompt": "View from airplane cockpit at night looking down at an enormous creature in the ocean, horror, 9:16 aspect ratio"},
            {"text": "It stood taller than Mount Everest. And it was still rising.", "prompt": "Impossibly large creature towering above storm clouds over the ocean, scale horror, cinematic, 9:16 aspect ratio"},
            {"text": "The creature did not attack. It simply... looked.", "prompt": "Close up of ancient massive creature eye reflecting city lights, calm but terrifying, 9:16 aspect ratio"},
            {"text": "Ancient symbols covered its skin. Scientists recognized them. Cave paintings. Found worldwide.", "prompt": "Glowing ancient symbols on the surface of a massive creature's skin, cosmic horror, cinematic, 9:16 aspect ratio"},
            {"text": "Our ancestors had seen this before. They left us warnings we never understood.", "prompt": "Ancient cave paintings showing massive sea creature and terrified humans running, torchlight, 9:16 aspect ratio"},
            {"text": "Every whale on Earth began swimming toward it. Every bird flew inland.", "prompt": "Hundreds of whales swimming together toward a massive silhouette, aerial cinematic, 9:16 aspect ratio"},
            {"text": "The electromagnetic pulse it released wiped every device on the coast.", "prompt": "City going dark in a wave of blackouts from the ocean inward, aerial night shot, 9:16 aspect ratio"},
            {"text": "One scientist managed to record one word before losing signal. Remember.", "prompt": "Scientist holding a crackling radio with static, dark emergency bunker, single word on screen, 9:16 aspect ratio"},
            {"text": "Military strikes had no effect. Missiles dissolved before reaching its skin.", "prompt": "Military missiles disintegrating before hitting a massive creature, futile military attack, cinematic, 9:16 aspect ratio"},
            {"text": "It turned and faced the deepest point of the ocean. Then it spoke.", "prompt": "Massive ancient creature facing the open ocean and releasing a deep resonant sound, cinematic, 9:16 aspect ratio"},
            {"text": "The sound it made registered on every seismograph on the planet simultaneously.", "prompt": "Seismograph needles going haywire all around the world simultaneously, global horror, 9:16 aspect ratio"},
            {"text": "And from seven other trenches across the world, something answered back.", "prompt": "World map showing seven points in the ocean simultaneously lighting up with activity, horror, 9:16 aspect ratio"},
        ],
    },
    # ── Part 3: The Reckoning ──────────────────────────────────────────────────
    {
        "output": "part3_reckoning.mp4",
        "scenes": [
            {"text": "Seven of them. Seven creatures. One for each continent.", "prompt": "Seven enormous ancient creatures rising from different oceans worldwide, epic cinematic horror, 9:16 aspect ratio"},
            {"text": "They had divided the Earth between them before humans ever existed.", "prompt": "Ancient map of Earth with seven territories marked, pre-human era, cosmic scale, 9:16 aspect ratio"},
            {"text": "Ancient texts had called them gods. Demons. Guardians.", "prompt": "Ancient stone tablets and scrolls depicting massive sea creatures worshipped by early humans, 9:16 aspect ratio"},
            {"text": "They were none of those things. They were the original owners.", "prompt": "Creature standing in the ocean looking down at human civilization with calm ancient eyes, 9:16 aspect ratio"},
            {"text": "Humanity had sixty hours. That was the message encoded in the pulse.", "prompt": "Scientists decoding an electromagnetic signal on screens, countdown clock, bunker setting, 9:16 aspect ratio"},
            {"text": "Every living translator on Earth agreed. Leave the ocean.", "prompt": "Translators and scientists in an emergency meeting all pointing to the same conclusion on a screen, 9:16 aspect ratio"},
            {"text": "We had been poisoning their home for three hundred years.", "prompt": "Ocean filled with pollution, plastic, oil spills seen from underwater looking up, somber cinematic, 9:16 aspect ratio"},
            {"text": "The creatures did not want war. They wanted the ocean back.", "prompt": "Ancient creature looking at ocean pollution with sorrowful ancient eyes, emotional cinematic, 9:16 aspect ratio"},
            {"text": "World leaders met in an emergency summit lasting eleven minutes.", "prompt": "World leaders at emergency summit table, tense expressions, flags, dark room, cinematic, 9:16 aspect ratio"},
            {"text": "The decision was unanimous. For the first time in human history.", "prompt": "World leaders all nodding in agreement, rare moment of unity, dramatic lighting, 9:16 aspect ratio"},
            {"text": "Every offshore platform. Every submarine. Every ship. Recalled.", "prompt": "Oil rigs being abandoned, ships turning back to shore, submarines surfacing, cinematic montage, 9:16 aspect ratio"},
            {"text": "The creatures watched. They did not move.", "prompt": "Seven massive creatures standing still in the ocean watching human ships retreat, dawn light, 9:16 aspect ratio"},
            {"text": "On the sixty-first hour, the first creature turned and descended.", "prompt": "Massive ancient creature slowly sinking back beneath the ocean surface at golden hour, cinematic, 9:16 aspect ratio"},
            {"text": "One by one, they returned to the dark. Back to the deep.", "prompt": "Sequence of enormous creatures slowly descending back into the ocean depths, peaceful, cinematic, 9:16 aspect ratio"},
            {"text": "The ocean was theirs again. And they would be watching. Always watching.", "prompt": "Calm empty ocean surface at sunrise, but deep below two massive glowing eyes watching upward, 9:16 aspect ratio"},
        ],
    },
]

# Active part to generate — change index to run a different part
ACTIVE_PART = 0  # 0=Part1, 1=Part2, 2=Part3

scenes = PARTS[ACTIVE_PART]["scenes"]


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
        PARTS[ACTIVE_PART]["output"],
    ]

    print("    Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("    FFmpeg stderr:\n", result.stderr)
        raise RuntimeError("FFmpeg failed — see stderr above.")

    print(f"    Saved {PARTS[ACTIVE_PART]['output']}")


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
        print(f"\nDone! Final video: {PARTS[ACTIVE_PART]['output']}")
    except Exception as e:
        print(f"\nPipeline error: {e}")
        raise
