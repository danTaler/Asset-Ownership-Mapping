FROM registry.redhat.io/ubi8/python-39:latest
ENV REQUESTS_CA_BUNDLE=

COPY ./src $APP_ROOT/src
COPY ./scripts $APP_ROOT/scripts
COPY ./scripts/container-entrypoint $APP_ROOT/bin/container-entrypoint

USER 0
RUN \
  dnf upgrade -y && \
  curl -o /etc/pki/ca-trust/source \
     && \
  curl -o /etc/pki/ca-trust/source/ \
    && \
  update-ca-trust && \
  cd $APP_ROOT && ./scripts/container-install && rm -rf $APP_ROOT/scripts && \
  chown -R root:root $APP_ROOT && chmod -R a+rX,go-w,u+w $APP_ROOT && \
  dnf clean all && rm -rf /var/cache /var/log/dnf* /var/log/yum.*

ENTRYPOINT ["container-entrypoint"]
