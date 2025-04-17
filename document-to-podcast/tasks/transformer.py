from flytekit import ContainerTask, FlyteFile, kwtypes

transform_document = ContainerTask(
    name="transform_document",
    image="dpoulopoulos/kfp-transformer:c5b697f",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    command=["python"],
    args=[
        "transformer.py",
        "--file", "{{ .inputs.file }}",
        "--file-type", "{{ .inputs.file_type }}",
        "--output", "{{ .outputs.processed_document }}",
    ],
    inputs=kwtypes(
        file=FlyteFile,
        file_type=str,
    ),
    outputs=kwtypes(processed_document=FlyteFile),
    cache=False,
)
