import getpass
import glob
import math
import os
import time
from datetime import datetime
from string import digits

import pdfplumber as plumber
from PyPDF2 import PdfFileMerger


def do_combine():
    start = datetime.now()
    start_date_str = start.strftime("%Y%m%d")
    start_time_str = start.strftime("%I.%M.%S%p")
    long_time_str = start.strftime("%y%m%d%I%M")

    log_text = ""
    print("OPERATION REPORT \n================\n")
    log_text += "OPERATION REPORT \n================\n\n"

    print(f"[{start_time_str}] Operation started\n")
    log_text += f"[{start_time_str}] Operation started\n"

    reports_path = input("Path to Reports folder: ")
    photos_path = input("Path to Photos folder: ")
    dest_folder = "\\".join(reports_path.split('\\')
                            [:-1]) + '\\' + long_time_str + '_' + 'COMBINED'

    def reports():
        return glob.glob(reports_path + '/*.pdf')

    def photos():
        return glob.glob(photos_path + '/*.pdf')

    for file in reports() + photos():
        os.rename(file, file.upper().replace("PDF", "pdf"))

    for file in reports() + photos():
        os.rename(file, " ".join(file.split()))

    for file in reports():
        os.rename(file, file.replace("LTD", "LIMITED"))

    report_list = []
    for file in reports():
        report_list.append(" ".join(file.split('\\')[-1].split(' ')[-2:]))

    photo_list = []
    for file in photos():
        photo_list.append(file.split('\\')[-1])

    def is_flagged(str):
        return str.replace(".pdf", "").endswith("-") or str.replace(".pdf", "").endswith("=")

    flagged_reports = [file for file in report_list if is_flagged(file)]
    flagged_photos = [file for file in photo_list if is_flagged(file)]
    unmatched_reports = [file for file in sorted(set(report_list).difference(photo_list)) if not is_flagged(file)]
    unmatched_photos =  [file for file in sorted(set(photo_list).difference(report_list)) if not is_flagged(file)]

    if unmatched_reports:
        log_text += "\nReports without matching photos\n"
        print(str(len(unmatched_reports))+" reports without matching photos. Skipped.")
        for i in range(len(unmatched_reports)):
            log_text += f"{i+1}. {unmatched_reports[i]}\n"

    if unmatched_photos:
        log_text += "\nPhotos without matching reports\n"
        print(str(len(unmatched_photos))+" photos without matching reports. Skipped.")
        for i in range(len(unmatched_photos)):
            log_text += f"{i+1}. {unmatched_photos[i]}\n"

    if flagged_reports:
        log_text += "\nFlagged reports found. Skipped.\n"
        print("\n" + str(len(flagged_reports)) +" Flagged reports found. Skipped.")
        for i in range(len(flagged_reports)):
            print(f"{i+1}. {flagged_reports[i]}")
            log_text += f"{i+1}. {flagged_reports[i]}\n"

    if flagged_photos:
        log_text += "\nFlagged photos found. Skipped.\n"
        print("\n"+str(len(flagged_photos)) + " Flagged photos found. Skipped.")
        for i in range(len(flagged_photos)):
            print(f"{i+1}. {flagged_photos[i]}")
            log_text += f"{i+1}. {flagged_photos[i]}\n"

    photo_set = []
    report_set = []


    for report in reports():
        if not is_flagged(report):
            for photo in photos():
                if not is_flagged(photo):
                    if report.find(photo.split("\\")[-1].split('.')[0]) > -1:
                        report_set.append(report)
                        photo_set.append(photo)

    if not unmatched_reports and not unmatched_photos:
        print(
            f"{str(len(report_set))} reports have been matched with their photo files"
        )
        log_text += f"{str(len(report_set))} reports have been matched with their photo files"
    else:
        print(
            f"\n\n{str(len(report_set))}/{str(len(reports()))} reports were successfully matched with photo files\n\n\u203AWorking..."
        )
        log_text += f"\n\n{str(len(report_set))}/{str(len(reports()))} reports were successfully matched with photo files\n\n\u203AWorking..."

    # Extract report content
    reports_content = []
    folios = []
    reg_nos = []

    def now():
        return datetime.now()

    now_str = now().strftime("%I:%M:%S%p")
    print(f"\n[{now_str}] Reading reports. Please wait...")
    log_text += f"\n\n[{now_str}] Reading reports. Please wait..."

    def extract_report_content():
        for report in report_set:
            with plumber.open(report) as pdf:
                page = pdf.pages[0]
                page_content = page.extract_text()
                reports_content.append(page_content)
        for text in reports_content:
            for line in text.split("\n"):
                if line.startswith("Ref. No."):
                    folio_mask = len(str(len(reports())))
                    folio = str(int(
                        line.split('/')[-2].split('-')[-1])).zfill(folio_mask)
                    folios.append(folio)
                elif line.startswith("Reg. No. "):
                    reg = line.split(" Steering ")[0].lstrip("Reg. No. ")
                    reg_nos.append(reg)

    extract_report_content()

    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    for i in range(len(report_set)):
        print("Combining: " + photo_set[i].split("\\")[-1])
        log_text += "\nCombining: " + photo_set[i].split("\\")[-1]
        merger = PdfFileMerger()
        merger.append(report_set[i])
        merger.append(photo_set[i])
        merger.write(dest_folder + '/' + report_set[i].split('\\')[-1])
        merger.close()

    combined = glob.glob(dest_folder + "/*.pdf")
    for i in range(len(combined)):
        report_path_partitioned = combined[i].split("\\")
        report_name = report_path_partitioned[-1]
        clean_report_name = report_name.lstrip(digits + ". ")
        new_name = dest_folder + "/" + folios[i] + ". " + clean_report_name
        os.rename(combined[i], new_name)

    # print("\nCreating fleet binder...")
    # log_text += "\nCreating fleet binder..."
    # combined = glob.glob(dest_folder + "/*.pdf")
    # binder = PdfFileMerger()
    # for i in range(len(combined)):
    #     binder.append(sorted(combined)[i])
    # binder.write(dest_folder + "/Fleet.temp.pdf")
    # binder.close()

    # with plumber.open(dest_folder + "/Fleet.temp.pdf") as pdf:
    #     fleet_binder = PdfFileMerger()
    #     fleet_binder.append(dest_folder + "/Fleet.temp.pdf")
    #     for page in pdf.pages:
    #         content = page.extract_text()
    #         for line in content.split("\n"):
    #             if line.startswith("Reg. No. "):
    #                 the_reg_no = line.split(" Steering ")[0].lstrip(
    #                     "Reg. No. ")
    #                 the_page = pdf.pages.index(page)
    #                 fleet_binder.addBookmark(the_reg_no, the_page)
    #     fleet_binder.write(dest_folder + "/Fleet Binder.pdf")
    #     fleet_binder.close()

    # os.remove(dest_folder + "/Fleet.temp.pdf")

    now_str = now().strftime("%I:%M:%S%p")

    end = datetime.now()

    def get_duration():
        diff = round((end - start).total_seconds())
        if diff < 2:
            return "1 second"
        elif diff < 60:
            return f"{round(diff)} seconds"
        elif diff > 60 and diff < 120:
            return f"{math.floor(diff / 60)} minute and {diff % 60} seconds"
        else:
            return f"{math.floor(diff / 60)} minutes and {diff % 60} seconds"

    now = datetime.now()
    now_str = now.strftime("%I:%M:%S%p")
    print(f"[{now_str}] Process Complete!!!")
    log_text += f"\n\n[{now_str}] Process Complete!!!"
    log_text += (
        f"\nYou processed {str(len(report_set))} reports in {get_duration()} \u263A"
    )

    print(f"\n\nMade in Kenya with code and caffeine by @kimuyuvictor")
    log_text += f"\n\nMade in Kenya with code and caffeine by @kimuyuvictor"

    log_file = open(f"{dest_folder}/{start_date_str}_[{start_time_str}].log",
                    "w",
                    encoding="utf-8")
    log_file.write(log_text)
    log_file.close()

    os.startfile(os.path.realpath(dest_folder + "/"))
    # os.startfile(os.path.realpath(dest_folder + "/Fleet Binder.pdf"))
    time.sleep(2)
    os.startfile(
        os.path.realpath(
            f"{dest_folder}/{start_date_str}_[{start_time_str}].log"))


suffix_source = int(datetime.now().strftime("%y%m%d%I%M") +
                    str(datetime.now().isocalendar()[1]))
suffix = str(math.radians(suffix_source))[-4:][::-1]


# def exec_combine():
#     combiner = getpass.getpass(r"_ ")
#     if combiner == suffix:
#         do_combine()
#     else:
#         print("Error. Terminating Process...")
#         time.sleep(3)


# exec_combine()

do_combine()
