Ansible Docker Buildblocks
==========================

Build automation helpers for docker images, using a common base image.

Gentoo is the only supported container OS at the moment, but the playbook should still be useful as a starting point for other distributions.

Gentoo
------

The top-level directory contains build include files (`_docker_gentoo_*`) for gentoo-based docker images. 
Prior to using these includes, a gentoo base image must be built.

### Building the Base Image

Run `ansible-playbook docker_gentoobase.yml` to build the gentoo image on which all gentoo containers will be based on. 
The image will be called `gentoobase`. Settings are defined in the vars section of `docker_gentoobase.yml`. 
They can be overriden in the `hosts` file (see `hosts.example`) or in `group_vars/all`.

### Building Derived Images

In order to use the gentoo build files, you have to include them in your Ansible playbook.
The easiest way is to checkout this project alongside your playbook and symlink the build files to the top-level directory of your playbook (where the `roles` directory resides). Like that:

    .
    ├── buildblocks
    ├── docker
    └── playbook
        ├── _docker_gentoo_build.yml -> ../buildblocks/_docker_gentoo_build.yml
        ├── _docker_gentoo_finish_image.yml -> ../buildblocks/_docker_gentoo_finish_image.yml
        ├── _docker_gentoo_prepare_build.yml -> ../buildblocks/_docker_gentoo_prepare_build.yml
        ├── group_vars
        └── roles
            └── yourrole


For docker images with only one ansible role on top of gentoobase:
-   include `_docker_build.yml` somewhere in your playbook
-   set the variable `name` to the name of the role that should be applied.
-   create a Dockerfile in ../docker/{{ role name }} 

The location of the Dockerfile directory can be changed by setting `dockerfile_path`.
You can put additional commands in the Dockerfile. The file must contain the following line:

    FROM intermediate_gentoo_{{ role name }}

Running your playbook will start a build container from the gentoo base image and apply the specified role to it.
The state of the container will be commited to an intermediate image.
Finally, a image called `gentoo_{{ role name }}` will be built on top of the intermediate image by using the Dockerfile you created.

For more complex scenarios, have a look at the contents of `_docker_build.yml` as inspiration. Have fun :)


