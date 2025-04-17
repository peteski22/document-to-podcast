from flytekit import ContainerTask, FlyteFile, kwtypes

performer = ContainerTask(
    name="performer",
    image="dpoulopoulos/kfp-performer:c5b697f",
    command=["python"],
    args=[
        "performer.py",
        "--input", "{{ .inputs.podcast_script }}",
        "--output", "{{ .outputs.podcast }}",
        "--voice-profiles", "{{ .inputs.host_voice_profile }}", "{{ .inputs.cohost_voice_profile }}",
        "--file-type", "{{ .inputs.file_type }}",
    ],
    inputs=kwtypes(
        podcast_script=FlyteFile,
        host_voice_profile=str,
        cohost_voice_profile=str,
        file_type=str,
    ),
    outputs=kwtypes(podcast=FlyteFile),
    #requests={"nvidia.com/gpu": "1"},
    cache=False,
)
