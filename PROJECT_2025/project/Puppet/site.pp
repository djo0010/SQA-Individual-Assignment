# uses the keystone packages
# to ensure that we use the latest precise packages
Exec { logoutput => 'on_failure' }

node 'glance_keystone_mysql' {
  class { '::mysql::server': }
  class { '::keystone':
    debug        => true,
    catalog_type => 'sql',
    admin_token => Deferred('vault_lookup::lookup', ['SECRET_PATH_84570/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::keystone::db::mysql':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_69952/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::keystone::roles::admin':
    email    => 'test@puppetlabs.com',
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_55561/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::api':
    debug               => true,
    auth_type => Deferred('vault_lookup::lookup', ['SECRET_PATH_26706/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_tenant => Deferred('vault_lookup::lookup', ['SECRET_PATH_80887/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_user => Deferred('vault_lookup::lookup', ['SECRET_PATH_61735/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_password => Deferred('vault_lookup::lookup', ['SECRET_PATH_3048/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_25759/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::backend::file': }

  class { '::glance::db::mysql':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_50158/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    dbname   => 'glance',
    user     => 'glance',
    host     => '127.0.0.1',
    # allowed_hosts = undef,
    # $cluster_id = 'localzone'
  }

  class { '::glance::registry':
    debug               => true,
    auth_type => Deferred('vault_lookup::lookup', ['SECRET_PATH_62251/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_tenant => Deferred('vault_lookup::lookup', ['SECRET_PATH_13336/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_user => Deferred('vault_lookup::lookup', ['SECRET_PATH_61405/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    keystone_password => Deferred('vault_lookup::lookup', ['SECRET_PATH_9380/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_1651/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::keystone::auth':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_1166/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
}

node default {
  fail("could not find a matching node entry for ${clientcert}")
}