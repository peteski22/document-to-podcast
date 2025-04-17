from flytekit import ContainerTask, FlyteFile

download_document = ContainerTask(
    name="download_document",
    image="dpoulopoulos/kfp-downloader:c5b697f",
    command=["python"],
    args=[
        "downloader.py",
        "--url", "{{ .inputs.url }}",
        "--output", "{{ .outputs.html_file }}",
        "--overwrite"
    ],
    inputs={
        "url": str,
    },
    outputs={
        "html_file": FlyteFile,  # HTML file
    },
    cache=False,
)
