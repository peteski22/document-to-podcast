from flytekit import ContainerTask, FlyteFile

transform_document = ContainerTask(
    name="transform_document",
    image="dpoulopoulos/kfp-transformer:c5b697f",
    command=["python"],
    args=[
        "transformer.py",
        "--input", "{{ .inputs.html_file }}",
        "--output", "{{ .outputs.processed_document }}",
        "--file-type", "{{ .inputs.file_type }}"
    ],
    inputs={
        "html_file": FlyteFile,
        "file_type": str,
    },
    outputs={
        "processed_document": FlyteFile,
    },
    cache=False,
)
