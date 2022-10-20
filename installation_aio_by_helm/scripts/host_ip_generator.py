#!/usr/bin/env python

from cloudify.state import ctx_parameters as inputs
from cloudify import ctx


if __name__=='__main__':
    ingress = dict(inputs.get('INGRESS'))
    ctx.instance.runtime_properties["HOST_ADDR"] = ingress['ip'] or ingress['hostname']
