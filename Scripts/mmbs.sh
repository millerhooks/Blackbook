#!/usr/bin/env bash
#
#   Mutual Mobile - Server Bootstrap
#   Copyright (c)2010
#
#

trap 'exit 1' TERM KILL INT QUIT ABRT


##
#   Configurations
##
TMPDIR='/tmp'
LOGFILE="${TMPDIR}/mm_bootstrap.log"

FLUP_VER='1.0.2'
FLUP_URL='http://www.saadi.com/software/flup/dist'

HQ_DC='dc=hq,dc=mutualmobile,dc=com'
HQ_IP='71.42.72.90'
HQ_DN='uid=proxyuser,cn=users,dc=hq,dc=mutualmobile,dc=com'
HQ_PW='a01aOYEsR0hzQ9IFl9LvT5ODNAQLao7L0Hjla8XYOWROoVXhkMFWQFLv1S0XqOQ'

PGSQL_VER='8.4'

##
#   Reporting Functions
##

error() {
    echo "!!! $*" 1>&2;
}

info() {
    echo "* $*";
    echo "[`date "+%c"`] $*" >> $LOGFILE
}

print_help() {
    prog=`echo $0 | sed 's/\.\///'`
    actions=`get_actions`

cat <<EOF
    Usage : ${prog} [action]
    Actions : ${actions}
EOF


}

get_actions() {
    all_actions=`grep ^function $0`

    IFS=$'\n'
    for a in $all_actions
    do
        cur_action=`echo $a | sed 's/function bootstrap_//'`
        cur_action=`echo $cur_action | sed 's/() {//'`

        actions="$actions $cur_action"
    done
    IFS=$' '

    echo $actions
}


install_packages() {
    system_packages="binutils emacs man screen vim \
        nfs-common autofs openntpd libpam-ldap libnss-ldap ldap-utils \
        nss-updatedb python-software-properties"

    python_packages="python python-docutils python-setuptools \
        python-pycurl python-beautifulsoup python-crypto"

    pgsql_packages="postgresql-server-dev-${PGSQL_VER}"
    postgis_packages="postgresql-${PGSQL_VER}-postgis python-gdal \
        libgeoip1 gdal-bin python-psycopg2 libgdal1-1.6.0 proj proj-bin"



    case $1 in
        update)
            apt-get -y -q update 2>&1 >> $LOGFILE
            apt-get -y -q --install-recommends dist-upgrade 2>&1 >> $LOGFILE
            ;;

        system)
            apt-get -y -q --install-recommends install \
                $system_packages
            ;;

        postgis)
            apt-get -y -q --install-recommends install \
                $pgsql_packages $postgis_packages
            ;;
    esac
}


ldap_config() {
    files="/etc/ldap.conf /etc/pam.d/common-account /etc/pam.d/common-auth \
        /etc/pam.d/common-password /etc/pam.d/common-session"

    for file in $files; do
        if [ -f $file ]; then
            mv $file $file-orig
        fi
    done

    nss_file=/etc/nssswitch.conf
    sed -i 's/passwd:/#passwd:/g' $nss_file
    sed -i 's/group:/#group:/g' $nss_file
    sed -i 's/shadow:/#shadow:/g' $nss_file

    #ldap_config_nsswitch
    ldap_config_ldap
    ldap_config_pam
}

ldap_config_nsswitch() {
cat >> /etc/nsswitch.conf <<EOF
##  Added by Mutual Mobile, Inc. Bootstrap

passwd:     files ldap
group:      files ldap
shadow:     files ldap
EOF
}

ldap_config_ldap() {
    ignore_users="backup,bin,daemon,games,gnats,irc,libuuid,list,lp,mail"
    ignore_users="${ignore_users},man,news,proxy,root,sshd"

cat > /etc/ldap.conf <<EOF
base $HQ_DC
uri ldap://$HQ_IP/
#host $HQ_IP
#binddn $HQ_DN
#bindpw $HQ_PW
ldap_version 3
pam_filter !(uid=root)
pam_passwd md5
nss_initgroups_ignoreusers $ignore_users
EOF
}

ldap_config_pam() {
cat > /etc/pam.d/common-account <<EOF
account sufficient pam_ldap.so
account required pam_unix.so
EOF

cat > /etc/pam.d/common-auth <<EOF
auth sufficient pam_ldap.so
auth required pam_unix.so
EOF

cat > /etc/pam.d/common-password <<EOF
password sufficient pam_ldap.so md5
password required pam_unix nullok obscure md5
EOF

cat > /etc/pam.d/common-session <<EOF
session required pam_mkhomedir.so skel=/etc/skel umask=0022
session sufficient pam_ldap.so
session required pam_unix.so
EOF
}

homedir_config() {
cat >> /etc/auto.master <<EOF
##  Added by Mutual Mobile, Inc. Bootstrap
/Users/hq /etc/auto.home
EOF

cat > /etc/auto.home <<EOF
* hq.mutualmobile.com:/Users/&
EOF
}



##
#   Bootstrap Functions
##

function bootstrap_system() {
    info 'Updating the package system'
    install_packages 'update'
    info 'Completed'

    info 'Installing base system packages'
    install_packages 'system'
    info 'Completed'

    info "Updating the system's timezone"
    if [ -e /etc/localtime ]; then
        mv /etc/localtime /etc/localtime-orig
    fi

    ln -s /usr/share/zoneinfo/US/Central /etc/localtime
    info 'Completed'

    info 'Configuring LDAP authentication'
    ldap_config
    info 'Completed'



}


function bootstrap_postgis() {
    info 'Installing required packages'
    install_packages 'postgis'
    info 'Completed'

    info 'Creating spatial database template'
    SQL_PATH=/usr/share/postgresql/${PGSQL_VER}/contrib
    
    main_commands=(
        "createdb -T template0 -E UTF8 template_postgis"
        "createlang -d template_postgis plpgsql"
        "psql -d postgres -c \"UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';\""
        "psql -d template_postgis -f $SQL_PATH/postgis.sql"
        "psql -d template_postgis -f $SQL_PATH/spatial_ref_sys.sql"
        "psql -d template_postgis -c \"GRANT ALL ON geometry_colums TO PUBLIC;\""
        "psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\""
        )

    for command in $(seq 0 $((${#main_commands[@]} - 1)))
    do
        su postgres -c "${main_commands[$command]}"
    done

    info 'Completed'

}

##
#   Handle User Activity
##

if [ -z "$1" ]; then
    print_help
    exit 1
fi

TARGET=${1}

if [[ $(type -t bootstrap_${TARGET}) != "function" ]]; then
    error "Invalid bootstrap target : ${TARGET}"
    exit 1
fi

info "Starting procedure for ${TARGET}"
bootstrap_${TARGET}
