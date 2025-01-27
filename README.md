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
    -v Version of the randomizer to generate with, default is 'v8.2'
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
usage: linkspocket [-h] -R REF [--http PROTO] [-Q] {push,pull} ...

positional arguments:
  {push,pull}
    push             Push a generated seed to the registry
    pull             Pull a generated seed from the registry

options:
  -h, --help         show this help message and exit
  -R REF, --ref REF  OCI reference, e.g myregistry.tld:5000/namespace:tag
  --http PROTO       Use plaintext HTTP instead of HTTPS to converse with registry
  -Q, --stfu         Don't output to console
```

This packages an output directory with at least a settings file in it into an
OCI artifact and push it to to where ever `--ref` specifies. No dependencies,
just run it -- well assuming you have an OCI registry available.



### Pushing

```
python3 -m linkspocket push -h
usage: linkspocket push [-h] -d SRC [-A]

Push a generated seed to the registry

options:
  -h, --help            show this help message and exit
  -d SRC, --seed-dir SRC
                        Path to directory containing zootr artifacts
  -A, --autotag         Automatically generate tag from seed hash, cedes to explicit tag in --ref

```

Example:

```bash
# tag manifest based on seed hash
python3 -m linkspocket -R my-oci-registry/zootr-seeds push -A -d ${SEEDHOME}/big-magic-beans-skull-token-saw-longshot/
# explicitly tag manifest
python3 -m linkspocket -R my-oci-registry/zootr-seeds:the-explicit-tag push -d ${SEEDHOME}/big-magic-beans-skull-token-saw-longshot/
```

### Pulling

```
python3 -m linkspocket pull -h
usage: linkspocket pull [-h] -o OUT [-C]

Pull a generated seed from the registry

options:
  -h, --help            show this help message and exit
  -o OUT, --output OUT  Output directory
  -C, --clean           Ensure output directory is empty before pulling
```

Example:

```bash
python3 -m linkspocket -R my-oci-registry/zootr-seeds:the-explicit-tag pull -C --out ../.artifacts/pulled
```

TODO:
- [x] Probably don't hardcode http
- [ ] Registry auth :sob:
- [ ] View stored seeds
