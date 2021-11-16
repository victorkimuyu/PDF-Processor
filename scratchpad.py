from glob import glob

reports_path = 'd:\\Dev\\Systems\\PDF_Merge\\DOCUMENTS\\REPORTS'
photos_path = 'd:\\Dev\\Systems\\PDF_Merge\\DOCUMENTS\\PHOTOS'


def reports():
    return glob(reports_path + '/*.pdf')


def photos():
    return glob(photos_path + '/*.pdf')

report_list = [" ".join(file.split('\\')[-1].split(" ")[-2:]) for file in reports()]
photo_list = [file.split('\\')[-1] for file in photos()]


flagged_reports = [file for file in report_list if (file.find("--") or file.find("=")) != -1]
flagged_photos = [file for file in photo_list if (file.find("--") or file.find("=")) != -1]

print(flagged_reports)