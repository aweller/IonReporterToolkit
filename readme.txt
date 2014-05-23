
#######################################################################################
Ion Reporter Toolkit
#######################################################################################

These scripts provide a way to move data (vcfs/bams) to and from the IonReporter 4.0 cloud platform.
They have been written for version 4.0. Any version changes might well break the scripts, you need to
at least adjust the URLs and tokens.

#######################################################################################
Download vcfs from IR

This is the largest script because the process of downloading is a bit complicated.

You need to have a list of the analysis names you want to download. In IR1.6. there was a functionality to export a big spreadsheet of all analysis together with metadata.
Unfortunately this is gone in IR4.0. The silly solution for now is to set the "View Analysis" pane in IR to show 100 analysis at a time and then simply copy+paste them to a text editor.

Per analysis, the script will go through these steps:
1. Download a json containing metadata and URLs for the actual analysis datafiles such as the vcfs.
2. Use the URL for unfiltered variants to download a zip of vcfs and additional metadata files (e.g. workflows used etc.).
3. Unzip the zip.

#######################################################################################
Download bams from IR

The scripts in this folder don't currently work because they are still setup for Ion Reporter 1.6
To repair them you'd need to fetch the correct download URL from the IR help pages on the API and
add a valid IR4.0 token.

The script move_bam_from_IR16_to_IR40.py is an extension of the other scripts. It not only fetches bams from IR (like the others)
but also reuploads them using the Lifetech-provided IonReporterUploader. It might become useful if for some reason it might be necessary to pull
out bams and reupload them to a new version of IR.

#######################################################################################
IR <> Oracle integration

This script is supposed to allow a transfer of vcfs into an Oracle DB by downloading vcfs from IR and directly uploading them into a DB. 

I added them to have a complete archive, but unfortunately I don't know how to use them myself as they were written entirely by Joe Wood.
You can contact him at "firstname [dot] lastname [at] lifetech [dot] com"