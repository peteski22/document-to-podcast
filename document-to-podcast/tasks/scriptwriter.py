from flytekit import ContainerTask, FlyteFile, kwtypes

scriptwriter = ContainerTask(
    name="scriptwriter",
    image="dpoulopoulos/kfp-scriptwriter:c5b697f",
    command=["python"],
    args=[
        "scriptwriter.py",
        "--input", "{{ .inputs.processed_document }}",
        "--output", "{{ .outputs.podcast_script }}",
        "--hosts", "{{ .inputs.host_name }}, {{ .inputs.cohost_name }}",
    ],
    inputs=kwtypes(
        processed_document=FlyteFile,
        host_name=str,
        cohost_name=str,
    ),
    outputs=kwtypes(podcast_script=FlyteFile),
    #requests={"nvidia.com/gpu": "1"},
    cache=False,
)
