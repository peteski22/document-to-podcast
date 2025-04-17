from flytekit import ContainerTask, FlyteFile, kwtypes


download_document = ContainerTask(
    name="download_document",
    image="dpoulopoulos/kfp-downloader:c5b697f",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    command=["python"],
    args=[
        "downloader.py",
        "--url", "{{ .inputs.url }}",
        "--output", "{{ .outputs.downloaded_file }}",
        "--overwrite",
    ],
    inputs=kwtypes(url=str),
    outputs=kwtypes(downloaded_file=FlyteFile),
    cache=False,
)
