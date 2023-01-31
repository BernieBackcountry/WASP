from pdf2image import convert_from_path

import wasp_tool.utilities as utilities

     
path = utilities.get_project_path().joinpath('data', 'freq_plans')
for p in path.rglob("*"):
    print(p)
    pdfs = p.glob('*.pdf')
    for pdf in pdfs:
        pages = convert_from_path(pdf)
        for i, page in enumerate(pages):
            file_path = path.joinpath(p.name)
            file_name = p.name + "_" + str(i) + ".jpg"
            page.save(file_path / file_name, 'JPEG')
