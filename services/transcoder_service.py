import re
import os
from pathlib import Path
from google.cloud.video import transcoder_v1
from google.cloud.video.transcoder_v1.types import Job, JobConfig

PROJECT_ID = "kamronlessonbot"
LOCATION = "us-central1"
OUTPUT_BUCKET = "kamronlessonbot.appspot.com"

CREDENTIALS_PATH = Path(__file__).parent.parent.joinpath("transcoder_service_account.json")

os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(CREDENTIALS_PATH))

client = transcoder_v1.TranscoderServiceClient(
    client_options={"api_endpoint": "transcoder.googleapis.com"},
    transport="rest",
)

def firebase_url_to_gcs_uri(firebase_url: str) -> str:
    match = re.search(r"/b/([^/]+)/o/([^?]+)", firebase_url)
    if not match:
        raise ValueError(f"Firebase URL formatini tanib bo'lmadi: {firebase_url}")
    bucket = match.group(1)
    path = match.group(2).replace("%2F", "/")
    return f"gs://{bucket}/{path}"

def build_abr_ladder_config(input_uri: str) -> JobConfig:
    return JobConfig(
        elementary_streams=[
            transcoder_v1.ElementaryStream(
                key="video-1080p",
                video_stream=transcoder_v1.VideoStream(
                    h264=transcoder_v1.VideoStream.H264CodecSettings(
                        height_pixels=1080,
                        width_pixels=1920,
                        bitrate_bps=5_000_000,
                        frame_rate=30,
                        gop_duration="2s",
                        rate_control_mode="vbr",
                        preset="medium",
                    )
                ),
            ),
            transcoder_v1.ElementaryStream(
                key="video-720p",
                video_stream=transcoder_v1.VideoStream(
                    h264=transcoder_v1.VideoStream.H264CodecSettings(
                        height_pixels=720,
                        width_pixels=1280,
                        bitrate_bps=2_500_000,
                        frame_rate=30,
                        gop_duration="2s",
                        rate_control_mode="vbr",
                        preset="medium",
                    )
                ),
            ),
            transcoder_v1.ElementaryStream(
                key="video-480p",
                video_stream=transcoder_v1.VideoStream(
                    h264=transcoder_v1.VideoStream.H264CodecSettings(
                        height_pixels=480,
                        width_pixels=854,
                        bitrate_bps=1_000_000,
                        frame_rate=30,
                        gop_duration="2s",
                        rate_control_mode="vbr",
                        preset="medium",
                    )
                ),
            ),
            transcoder_v1.ElementaryStream(
                key="audio-stream0",
                audio_stream=transcoder_v1.AudioStream(
                    codec="aac",
                    bitrate_bps=128_000,
                ),
            ),
        ],
        mux_streams=[
            transcoder_v1.MuxStream(
                key="hls-1080p",
                container="ts",
                elementary_streams=["video-1080p", "audio-stream0"],
            ),
            transcoder_v1.MuxStream(
                key="hls-720p",
                container="ts",
                elementary_streams=["video-720p", "audio-stream0"],
            ),
            transcoder_v1.MuxStream(
                key="hls-480p",
                container="ts",
                elementary_streams=["video-480p", "audio-stream0"],
            ),
        ],
        manifests=[
            transcoder_v1.Manifest(
                file_name="master.m3u8",
                type_=transcoder_v1.Manifest.ManifestType.HLS,
                mux_streams=["hls-1080p", "hls-720p", "hls-480p"],
            ),
        ],
    )

def create_transcode_job(input_uri: str, lesson_id: int) -> str:
    output_uri = f"gs://{OUTPUT_BUCKET}/my-zone-online/transcoder_lesson/{lesson_id}/"
    config = build_abr_ladder_config(input_uri)

    job = Job(input_uri=input_uri, output_uri=output_uri, config=config)
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"

    response = client.create_job(parent=parent, job=job)
    return response.name

def get_job_status(job_name: str) -> str:
    job = client.get_job(name=job_name)
    print(f"[transcoder service] job_name={job_name}, state={job.state.name}")
    return job.state.name  # PENDING / RUNNING / SUCCEEDED / FAILED

def hls_master_url(lesson_id: int) -> str:
    print(f"[transcoder service] lesson_id={lesson_id}")
    return f"https://storage.googleapis.com/{OUTPUT_BUCKET}/my-zone-online/transcoder_lesson/{lesson_id}/master.m3u8"
