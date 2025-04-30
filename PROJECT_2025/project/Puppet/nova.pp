# Configure the Nova service
#
# [*libvirt_rbd*]
#   (optional) Boolean to configure or not Nova
#   to use Libvirt RBD backend.
#   Defaults to false.
#
# [*libvirt_virt_type*]
#   (optional) Libvirt domain type. Options are: kvm, lxc, qemu, uml, xen
#   Defaults to 'qemu'
#
# [*libvirt_cpu_mode*]
#   (optional) The libvirt CPU mode to configure.
#   Possible values include custom, host-model, none, host-passthrough.
#   Defaults to 'none'
#
# [*volume_encryption*]
#   (optional) Boolean to configure or not volume encryption
#   Defaults to false.
#
# [*notification_topics*]
#   (optional) AMQP topic used for OpenStack notifications
#   Defaults to $::os_service_default.
#
class openstack_integration::nova (
  $libvirt_rbd         = false,
  $libvirt_virt_type   = 'qemu',
  $libvirt_cpu_mode    = 'none',
  $volume_encryption   = false,
  $notification_topics = $::os_service_default,
) {

  include ::openstack_integration::config
  include ::openstack_integration::params

  if $::openstack_integration::config::ssl {
    openstack_integration::ssl_key { 'nova':
      notify  => Service['httpd'],
      require => Package['nova-common'],
    }
    Exec['update-ca-certificates'] ~> Service['httpd']
  }

  $default_transport_url = os_transport_url({
    'transport' => $::openstack_integration::config::messaging_default_proto,
    'host'      => $::openstack_integration::config::host,
    'port'      => $::openstack_integration::config::messaging_default_port,
    'username'  => 'nova',
    'password' => Deferred('vault_lookup::lookup', ['SECRET_PATH_21341/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  })

  $notification_transport_url = os_transport_url({
    'transport' => $::openstack_integration::config::messaging_notify_proto,
    'host'      => $::openstack_integration::config::host,
    'port'      => $::openstack_integration::config::messaging_notify_port,
    'username'  => 'nova',
    'password' => Deferred('vault_lookup::lookup', ['SECRET_PATH_14180/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  })

  openstack_integration::mq_user { 'nova':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_14308/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    before   => Anchor['nova::service::begin'],
  }

  class { '::nova::db::mysql':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_4313/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::nova::db::mysql_api':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_63067/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  include ::nova::cell_v2::simple_setup

  # NOTE(aschultz): workaround for race condition for discover_hosts being run
  # prior to the compute being registered
  exec { 'wait-for-compute-registration':
    path        => ['/bin', '/usr/bin'],
    command     => 'sleep 10',
    refreshonly => true,
    notify      => Class['nova::cell_v2::discover_hosts'],
    subscribe   => Anchor['nova::service::end'],
  }

  class { '::nova::db::mysql_placement':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_9814/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::nova::keystone::auth':
    public_url   => "${::openstack_integration::config::base_url}:8774/v2.1",
    internal_url => "${::openstack_integration::config::base_url}:8774/v2.1",
    admin_url    => "${::openstack_integration::config::base_url}:8774/v2.1",
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_45288/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  if ($::os_package_type == 'debian') {
    class { '::nova::keystone::auth_placement':
      public_url   => "${::openstack_integration::config::base_url}:8778",
      internal_url => "${::openstack_integration::config::base_url}:8778",
      admin_url    => "${::openstack_integration::config::base_url}:8778",
      password => Deferred('vault_lookup::lookup', ['SECRET_PATH_59682/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    }
  } else {
    class { '::nova::keystone::auth_placement':
      public_url   => "${::openstack_integration::config::base_url}:8778/placement",
      internal_url => "${::openstack_integration::config::base_url}:8778/placement",
      admin_url    => "${::openstack_integration::config::base_url}:8778/placement",
      password => Deferred('vault_lookup::lookup', ['SECRET_PATH_1868/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    }
  }
  class { '::nova::keystone::authtoken':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_27736/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    user_domain_name     => 'Default',
    project_domain_name  => 'Default',
    auth_url => Deferred('vault_lookup::lookup', ['SECRET_PATH_80151/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    www_authenticate_uri => Deferred('vault_lookup::lookup', ['SECRET_PATH_55967/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    memcached_servers    => $::openstack_integration::config::memcached_servers,
  }
  class { '::nova':
    default_transport_url         => $default_transport_url,
    notification_transport_url    => $notification_transport_url,
    database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_89116/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    api_database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_84997/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    placement_database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_71372/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    rabbit_use_ssl                => $::openstack_integration::config::ssl,
    amqp_sasl_mechanisms          => 'PLAIN',
    use_ipv6                      => $::openstack_integration::config::ipv6,
    glance_api_servers            => "${::openstack_integration::config::base_url}:9292",
    debug                         => true,
    notification_driver           => 'messagingv2',
    notify_on_state_change        => 'vm_and_task_state',
    notification_topics           => $notification_topics,
  }
  class { '::nova::api':
    api_bind_address                     => $::openstack_integration::config::host,
    neutron_metadata_proxy_shared_secret => Deferred('vault_lookup::lookup', ['SECRET_PATH_9268/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    metadata_workers                     => 2,
    sync_db_api                          => true,
    service_name                         => 'httpd',
  }
  include ::apache
  class { '::nova::wsgi::apache_api':
    bind_host => $::openstack_integration::config::ip_for_url,
    ssl_key => Deferred('vault_lookup::lookup', ['SECRET_PATH_64937/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    ssl_cert  => $::openstack_integration::params::cert_path,
    ssl       => $::openstack_integration::config::ssl,
    workers   => '2',
  }
  if ($::os_package_type != 'debian') {
    class { '::nova::wsgi::apache_placement':
      bind_host => $::openstack_integration::config::ip_for_url,
      api_port  => '8778',
      ssl_key => Deferred('vault_lookup::lookup', ['SECRET_PATH_80851/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
      ssl_cert  => $::openstack_integration::params::cert_path,
      ssl       => $::openstack_integration::config::ssl,
      workers   => '2',
    }
  }
  class { '::nova::placement':
    auth_url => Deferred('vault_lookup::lookup', ['SECRET_PATH_88029/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_72215/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::nova::client': }
  class { '::nova::conductor': }
  class { '::nova::consoleauth': }
  class { '::nova::cron::archive_deleted_rows': }
  if $volume_encryption {
    $keymgr_api_class     = 'castellan.key_manager.barbican_key_manager.BarbicanKeyManager'
    $keymgr_auth_endpoint = "${::openstack_integration::config::keystone_auth_uri}/v3"
    $barbican_endpoint    = "${::openstack_integration::config::base_url}:9311"
  } else {
    $keymgr_api_class     = undef
    $keymgr_auth_endpoint = undef
    $barbican_endpoint    = undef
  }
  class { '::nova::compute':
    vnc_enabled                 => true,
    instance_usage_audit        => true,
    instance_usage_audit_period => 'hour',
    keymgr_api_class => Deferred('vault_lookup::lookup', ['SECRET_PATH_63496/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    barbican_auth_endpoint => Deferred('vault_lookup::lookup', ['SECRET_PATH_60773/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    barbican_endpoint           => $barbican_endpoint,
  }
  class { '::nova::compute::libvirt':
    libvirt_virt_type     => $libvirt_virt_type,
    libvirt_cpu_mode      => $libvirt_cpu_mode,
    migration_support     => true,
    # virtlock and virtlog services resources are not idempotent
    # on Ubuntu, let's disable it for now.
    # https://tickets.puppetlabs.com/browse/PUP-6370
    virtlock_service_name => false,
    virtlog_service_name  => false,
  }
  if $libvirt_rbd {
    class { '::nova::compute::rbd':
      libvirt_rbd_user        => 'openstack',
      libvirt_rbd_secret_uuid => Deferred('vault_lookup::lookup', ['SECRET_PATH_7140/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
      libvirt_rbd_secret_key => Deferred('vault_lookup::lookup', ['SECRET_PATH_41542/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
      libvirt_images_rbd_pool => 'nova',
      rbd_keyring => Deferred('vault_lookup::lookup', ['SECRET_PATH_19986/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
      # ceph packaging is already managed by puppet-ceph
      manage_ceph_client      => false,
    }
    # make sure ceph pool exists before running nova-compute
    Exec['create-nova'] -> Service['nova-compute']
  }
  class { '::nova::scheduler': }
  class { '::nova::scheduler::filter': }
  class { '::nova::vncproxy': }

  class { '::nova::network::neutron':
    neutron_auth_url => Deferred('vault_lookup::lookup', ['SECRET_PATH_26745/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    neutron_url           => "${::openstack_integration::config::base_url}:9696",
    neutron_password => Deferred('vault_lookup::lookup', ['SECRET_PATH_24355/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    default_floating_pool => 'public',
  }

  Keystone_endpoint <||> -> Service['nova-compute']
  Keystone_service <||> -> Service['nova-compute']
}