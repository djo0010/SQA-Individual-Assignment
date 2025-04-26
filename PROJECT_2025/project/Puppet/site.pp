# uses the keystone packages
# to ensure that we use the latest precise packages
Exec { logoutput => 'on_failure' }

node 'glance_keystone_mysql' {
  class { '::mysql::server': }
  class { '::keystone':
    debug        => true,
    catalog_type => 'sql',
    admin_token  => Deferred('vault_lookup::lookup', ["SECRET_PATH_14524/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }
  class { '::keystone::db::mysql':
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_99238/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }
  class { '::keystone::roles::admin':
    email    => Deferred('vault_lookup::lookup', ["SECRET_PATH_92240/hvs.GNVrHOS4F9QpkAfg2wSV1Vfr", 'http://127.0.0.1:8200']),
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_25424/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }
  class { '::glance::api':
    debug               => true,
    auth_type           => 'keystone',
    keystone_tenant     => 'services',
    keystone_user       => 'glance',
    keystone_password   => Deferred('vault_lookup::lookup', ["SECRET_PATH_34870/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
    database_connection => 'mysql+pymysql://glance:glance@127.0.0.1/glance',
  }
  class { '::glance::backend::file': }

  class { '::glance::db::mysql':
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_69379/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
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
    keystone_password   => Deferred('vault_lookup::lookup', ["SECRET_PATH_31379/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
    database_connection => 'mysql+pymysql://glance:glance@127.0.0.1/glance',
  }
  class { '::glance::keystone::auth':
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_56283/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }
}

node default {
  fail("could not find a matching node entry for ${clientcert}")
}
