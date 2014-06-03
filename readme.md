######################################################################
######################################################################
# ION REPORTER TOOLKIT
######################################################################
######################################################################

These scripts provide a way to move data (vcfs/bams) to and from the IonReporter 4.0 cloud platform. They have been written for version 4.0. Any version changes might well break the scripts, you need to at least adjust the URLs and tokens.

The scripts assume a standard installation of Python 2.7. If you're lacking any modules that it tries to import just install them with
"pip install {module}". If you dont have pip installed, use "apt-get install python-pip".

There are no scripts for uploading bams to IR, because this is handled either automatically by the Torrent Server or manually from the command line by the Lifetech tool "IonReporterUploader" which can be downloaded from within IR (click the button on the top right of the screen). When uploading bams, always make sure to upload unaligned bams (i.e. bams without a chromosome location for each read) as IR doesn't accept aligned bams. You can check each bam with "samtools view mybam.bam | less", if you don't see "chr3 12345" anywhere it's an unaligned bam.

All scripts assume that you run them on the commandline, ususally inside the directory that contains your input files. If you want to execute the scripts from an IDE, all you need to do is to change the parsing of command line arguments:
> input = sys.argv[1]

into e.g. a hardcoded filename

> input = "/home/andreas/input.txt"

######################################################################
## Download vcfs from IR
######################################################################

This is the largest script because the process of downloading is a bit complicated.

You need to have a list of the analysis names you want to download. In IR1.6. there was a functionality to export a big spreadsheet of all analysis together with metadata. Unfortunately this is gone in IR4.0. The silly solution for now is to set the "View Analysis" pane in IR to show 100 analysis at a time and then simply copy+paste them to a text editor.

Per analysis, the script will go through these steps:
1. Download a json containing metadata and URLs for the actual analysis datafiles such as the vcfs.
2. Use the URL for unfiltered variants to download a zip of vcfs and additional metadata files (e.g. workflows used etc.).
3. Unzip the zip.

Usage: 
> python RunIRVariantAnnotation.py input_file.txt

######################################################################
## Locate and copy bams on TS
######################################################################

This script helps in finding the correct bam for a Barcode/RunID combination and moving the bams to a new location. 

It parses a tab-seperated input file of the format

> Sample    Tumor/Normal    Barcode Run
>
> BC451-T-HP	T	    1	    OX1-317
>
> BC615-T-HP	T	    2	    OX1-311


then creates an output file each for
A) aligned bams for research use on another computer and
B) unaligned bams for upload to Ion Reporter.

The output files are meant to be executed as bash scripts.

You might need to modify 2 parts of this script:
1. the locations list, which is a list of all TS folder where bams might be kept (specific to the WTCHG Torrent Server)
2. the unifiy_sample_name function, which reformats sample names (specific to the WTCHG Quasar project)

Usage: 
> python locate_and_copy_bams_from_TS.py input_file.txt output_unaligned.sh output_aligned.sh

######################################################################
## Download bams from IR
######################################################################

The scripts in this folder don't currently work because they are still setup for Ion Reporter 1.6
To repair them you'd need to fetch the correct download URL from the IR help pages on the API and
add a valid IR4.0 token.

The script move_bam_from_IR16_to_IR40.py is an extension of the other scripts. It not only fetches bams from IR (like the others)
but also reuploads them using the Lifetech-provided IonReporterUploader. It might become useful if for some reason it might be necessary to pull
out bams and reupload them to a new version of IR.

######################################################################
## Compare Variant Callers
######################################################################

This script was written to make the switch to a new version of Ion Reporter easier. A new version of IR comes with a new version of the Torrent Variant Caller
algorithm which might call different variants, therefore the old and new variants need to be compared.

The script expects a folder of vcf files (+ their annotation tsvs) downloaded from IonReporter with the following filename format:

 - G153317Q_v2_IR16.vcf (+ G153317Q_v2_IR16.tsv)
 - G153317Q_v2_IR40.vcf (+ G153317Q_v2_IR40.tsv)

It pairwise compares the vcfs that differ only in the IR16/IR40 and creates several output files:
 - all positions
 - all variants (no ref positions)
 - actionable variants (only variants with protein impact)

The output for the actionable variants are then combined into one file ("cat \*action\* > all_Samples.tsv"), loaded into Excel and analysed by hand to explain the differences

Usage: 
> python CompareVCFs.py input_folder output_folder

##########################################################################################################################

Disclaimer:
This script is highly optimized for comparison on IR14 vs IR16 vs IR40.
New versions of IR will very likely break something due to new vcf fields, different annotation file layouts or similar.
Proceed with caution!

######################################################################
## IR <> Oracle integration
######################################################################

This script is supposed to allow a transfer of vcfs into an Oracle DB by downloading vcfs from IR and directly uploading them into a DB. 

I added them to have a complete archive, but unfortunately I don't know how to use them myself as they were written entirely by Joe Wood.
You can contact him at "firstname [dot] lastname [at] lifetech [dot] com"