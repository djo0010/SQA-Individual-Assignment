# Example: enabling magnum module in Puppet

  rabbitmq_user { 'magnum':
    admin    => true,
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_52287/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
    provider => 'rabbitmqctl',
    require  => Class['::rabbitmq'],
  }

  rabbitmq_user_permissions { 'magnum@/':
    configure_permission => '.*',
    write_permission     => '.*',
    read_permission      => '.*',
    provider             => 'rabbitmqctl',
    require              => Class['::rabbitmq'],
  }

  class { '::magnum::db::mysql':
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_11530/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }

  class { '::magnum::db':
    database_connection => Deferred('vault_lookup::lookup', ["SECRET_PATH_87324/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }

  class { '::magnum::keystone::domain':
    domain_password => Deferred('vault_lookup::lookup', ["SECRET_PATH_46265/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }

  class { '::magnum::keystone::authtoken':
    password => Deferred('vault_lookup::lookup', ["SECRET_PATH_86544/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
  }

  class { '::magnum::api':
    host => '127.0.0.1',
  }

  class { '::magnum::keystone::auth':
    password     => Deferred('vault_lookup::lookup', ["SECRET_PATH_94249/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
    public_url   => 'http://127.0.0.1:9511/v1',
    internal_url => 'http://127.0.0.1:9511/v1',
    admin_url    => 'http://127.0.0.1:9511/v1',
  }

  class { '::magnum':
    rabbit_host         => '127.0.0.1',
    rabbit_port         => '5672',
    rabbit_userid       => 'magnum',
    rabbit_password     => Deferred('vault_lookup::lookup', ["SECRET_PATH_76569/hvs.OaljJCdZZ56rwmoCOHvWiyPJ", 'http://127.0.0.1:8200']),
    rabbit_use_ssl      =>  false,
    notification_driver => 'messagingv2',
  }

  class { '::magnum::conductor':
  }

  class { '::magnum::client':
  }

  class { '::magnum::certificates':
    cert_manager_type => 'local'
  }

