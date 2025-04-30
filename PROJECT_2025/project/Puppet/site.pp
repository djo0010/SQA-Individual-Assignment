# uses the keystone packages
# to ensure that we use the latest precise packages
Exec { logoutput => 'on_failure' }

node 'glance_keystone_mysql' {
  class { '::mysql::server': }
  class { '::keystone':
    debug        => true,
    catalog_type => 'sql',
    admin_token => Deferred('vault_lookup::lookup', ['SECRET_PATH_57126/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::keystone::db::mysql':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_79391/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::keystone::roles::admin':
    email    => 'test@puppetlabs.com',
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_64631/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::api':
    debug               => true,
    auth_type           => 'keystone',
    keystone_tenant     => 'services',
    keystone_user       => 'glance',
    keystone_password => Deferred('vault_lookup::lookup', ['SECRET_PATH_36883/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_44364/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::backend::file': }

  class { '::glance::db::mysql':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_18463/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    dbname   => 'glance',
    user     => 'glance',
    host     => '127.0.0.1',
    # allowed_hosts = undef,
    # $cluster_id = 'localzone'
  }

  class { '::glance::registry':
    debug               => true,
    auth_type           => 'keystone',
    keystone_tenant     => 'services',
    keystone_user       => 'glance',
    keystone_password => Deferred('vault_lookup::lookup', ['SECRET_PATH_4584/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
    database_connection => Deferred('vault_lookup::lookup', ['SECRET_PATH_38973/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
  class { '::glance::keystone::auth':
    password => Deferred('vault_lookup::lookup', ['SECRET_PATH_54291/hvs.VFfZyxeBFW7L0N9mPxqsQqcj', 'http://127.0.0.1:8200']),
  }
}

node default {
  fail("could not find a matching node entry for ${clientcert}")
}