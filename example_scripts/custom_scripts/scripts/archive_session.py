#!/usr/bin/env python

'''
Program to take transcript and images to save in archive folder (archived_sessions)

TODO: Add argument for clobbering when archiving, option to overwrite an existing folder
'''

import os
import shutil
import argparse

ARCHIVE_PATH = "/home/vishnu/ros_ws/src/custom_scripts/archived_sessions"
IMAGES_PATH = "/home/vishnu/ros_ws/src/custom_scripts/images/session_history"
TRANSCRIPT_PATH = "/home/vishnu/ros_ws/src/custom_scripts/transcripts/log.json"

def archive_session(folder_name):
    if os.path.exists("/home/vishnu/ros_ws/src/custom_scripts/archived_sessions/{}".format(folder_name)):
        print("Error: folder exists.")
    else:
        os.makedirs("{}/{}".format(ARCHIVE_PATH, folder_name))
        shutil.copytree(IMAGES_PATH, "{}/{}/images".format(ARCHIVE_PATH, folder_name))
        shutil.copy(TRANSCRIPT_PATH, "{}/{}".format(ARCHIVE_PATH, folder_name))
        print("Saved last session transcript and images to archived_sessions/{}".format(folder_name))
        # for filename in os.listdir(IMAGES_PATH):
        #     file_path = "{}/{}".format(IMAGES_PATH, filename)
        #     os.unlink(file_path)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
		prog='archive_session.py',
		description='Saves log and images to archived_sessions',
		epilog='Made by Andrew Ge, SURF 2024'
	)
	
    parser.add_argument('foldername', help='Name of png file to be saved')
    args = parser.parse_args()

    archive_session(args.foldername)