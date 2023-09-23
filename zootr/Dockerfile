FROM python:3.11-slim-bookworm
ARG REF

COPY ./zootr-source/ /usr/lib/zootr
COPY ./zootr-source/bin/Decompress/Decompress /usr/bin/decompress
COPY --from="base" --chmod=777 entrypoint.sh /usr/bin/entrypoint

ENTRYPOINT ["/usr/bin/entrypoint"]
CMD ["-h"]
