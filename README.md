# linkspocket

Multipurpose, over engineered tool for OOTR seed storage. Named for the
location of starting items in OOTR.

## CLI Generation

Bash script wrapper that will create and use a container to create a zootr seed
and then copy the contents to the desired destination directory.

```
Usage linkspocket -r <path to oot rom> -o <directory to put output into>

    -h Show this message and exit
    -o Base output directory, may be absolute or relative to current directory
       This directory will be created if necessary
    -r Path to rom, may be absolute or relative to current directory
    -t Output files are placed in a directory with this name
       By default a tag is derived from the generated settings file
    -v Version of the randomizer to generate with, default is 'v7.1.0'
       If the version is not present, this script will attempt to build it first
       May be any 'commit-ish' (as defined by git) present in the OOTR repository

OOTR specific CLI options can be passed by providing -- and then the options.
A settings file is always generated.

Example usage:

    linkspocket -r ./my-rom.z64 -o ~/zootr-seeds/ -t my-seed -- --settings_string [omitted]

This would create a directory ~/zootr-seeds/my-seed from the specified rom and
settings string.
```

Pairs well with...

## OCI Client

```
python3 -m linkspocket -h
usage: linkspocket [-h] -d DIR -R REF [-Q]

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --seed-dir DIR
                        Path to directory containing zootr artifacts
  -R REF, --ref REF
  -Q, --stfu            For real, shut the fuck up
```

This packages an output directory with at least a settings file in it into an
OCI artifact and push it to to where ever `--ref` specifies. No dependencies,
just run it -- well assuming you have an OCI registry available.

TODO:
- [ ] Probably don't hardcode http
- [ ] Registry auth :sob:
- [ ] View stored seeds
