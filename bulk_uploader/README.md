# How to use

    python3 bulk_uploader.py --email=<email> --password=<password> \
    --directory=<upload directory> --channel=<service channel>

You can also use --token=<jwt token> instead of --email and --password

## Service Channel
Only 'yui' can use

## BPM, Scale in Title
If you set bpm, scale in the title, you can use meta information.

    [138 C] Sea Tides (Original Mix)

in this case, 138 and scale C is extracted, and upload this data.

If these tag is not, ignore this. No problem to upload.