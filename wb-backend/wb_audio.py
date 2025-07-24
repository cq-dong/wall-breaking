import pydub

def audio_length(audio_file):
    audio = pydub.AudioSegment.from_file(audio_file)
    return audio.duration_seconds

# 合并所有音轨到一个
def merge_audio_tracks(audio_file):
    audio = pydub.AudioSegment.from_file(audio_file)
    audio = audio.set_channels(1)
    return audio

# 查看音轨数
def get_audio_track_count(audio_file):
    audio = pydub.AudioSegment.from_file(audio_file)
    return audio.channels
