The scripts in this folder don't currently work because they are still setup for Ion Reporter 1.6
To repair them you'd need to fetch the correct download URL from the IR help pages on the API and
add a valid IR4.0 token.

The script move_bam_from_IR16_to_IR40.py is an extension of the other scripts. It not only fetches bams from IR (like the others)
but also reuploads them using the Lifetech-provided IonReporterUploader. It might become useful if for some reason it might be necessary to pull
out bams and reupload them to a new version of IR.