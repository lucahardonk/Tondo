import torch
import argparse
import sounddevice as sd
from transformers import AutoTokenizer
from parler_tts import ParlerTTSForConditionalGeneration, ParlerTTSStreamer
from threading import Thread

# Command line argument parsing
parser = argparse.ArgumentParser(description="Generate and play speech from text.")
parser.add_argument("text", type=str, help="Text to be spoken.")
args = parser.parse_args()

torch_device = "cuda:0"  # Use "cuda:0" for NVIDIA GPUs or "mps" for Mac
torch_dtype = torch.bfloat16
model_name = "parler-tts/parler-tts-mini-v1"
max_length = 50

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = ParlerTTSForConditionalGeneration.from_pretrained(model_name).to(torch_device, dtype=torch_dtype)

sampling_rate = model.audio_encoder.config.sampling_rate
frame_rate = model.audio_encoder.config.frame_rate

def generate(text, description, play_steps_in_s=1.5):
    play_steps = int(frame_rate * play_steps_in_s)
    streamer = ParlerTTSStreamer(model, device=torch_device, play_steps=play_steps)

    inputs = tokenizer(description, return_tensors="pt").to(torch_device)
    prompt = tokenizer(text, return_tensors="pt").to(torch_device)

    generation_kwargs = {
        "input_ids": inputs.input_ids,
        "prompt_input_ids": prompt.input_ids,
        #"attention_mask": inputs.attention_mask,
        "prompt_attention_mask": prompt.attention_mask,
        "streamer": streamer,
        "do_sample": True,
        "temperature": 1.0,
        "min_new_tokens": 10,
    }

    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    for new_audio in streamer:
        if new_audio.shape[0] == 0:
            break
        yield sampling_rate, new_audio

description = "Jon's talking clearly and smoothly"
chunk_size_in_s = 2.0

for (sampling_rate, audio_chunk) in generate(args.text, description, chunk_size_in_s):
    # Play audio chunk
    sd.play(audio_chunk, samplerate=sampling_rate)
    sd.wait()  # Wait until audio is done playing

