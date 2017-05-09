# wedos-miniweb-cli
tool to manage files on **miniweb** service provided by Wedos webhoster

### to do
* [ ] implement parameters
* [ ] single root file upload
* [ ] single non-root file upload
* [ ] all files upload
* [ ] zip download
* [ ] single root file download
* [ ] single non-root file download
* [ ] all files download
* [ ] single root file delete
* [ ] single non-root file delete
* [ ] all files delete

### parameters
draft

    -d --domain     remote web domain
    -p --path       local path to directory/file
    -u --upload     upload file(s)
    -s --single     single file operation
    -l --list       list remote files
    -z --zip        download all zipped files
       --download   download file(s)
       --delete     delete file(s)

### usage examples
draft

    wedos-miniweb-cli.py -d mydomain.eu -l
    wedos-miniweb-cli.py -d mydomain.eu -p /home/user/mydomain -u
    wedos-miniweb-cli.py -d mydomain.eu -p /home/user/mydomain.zip -z
    wedos-miniweb-cli.py -d mydomain.eu -p /home/user/mydomain/index.html -s -u
    wedos-miniweb-cli.py -d mydomain.eu -p /home/user/mydomain/files/photo.jpg -s -u
