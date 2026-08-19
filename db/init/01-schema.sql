CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    user_id VARCHAR(64) NOT NULL,
    display_name VARCHAR(128) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subscription_token CHAR(64) NOT NULL,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE KEY uq_users_user_id (user_id),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_subscription_token (subscription_token)
) ENGINE=InnoDB;


CREATE TABLE servers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    server_id VARCHAR(64) NOT NULL,

    host VARCHAR(255) NOT NULL,
    port SMALLINT UNSIGNED NOT NULL DEFAULT 443,

    encryption VARCHAR(32) NOT NULL DEFAULT '',
    flow VARCHAR(64) DEFAULT 'xtls-rprx-vision',

    transport_type VARCHAR(32) NOT NULL DEFAULT 'tcp',

    security VARCHAR(32) NOT NULL DEFAULT 'reality',

    sni VARCHAR(255) DEFAULT NULL,
    fingerprint VARCHAR(64) DEFAULT 'chrome',

    reality_public_key VARCHAR(255) DEFAULT NULL,
    reality_short_id VARCHAR(255) DEFAULT NULL,

    alpn VARCHAR(255) DEFAULT 'h2',

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    sort_order INT NOT NULL DEFAULT 0,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE KEY uq_servers_server_id (server_id),

    KEY idx_servers_enabled_sort (
        enabled,
        sort_order
    )
) ENGINE=InnoDB;


CREATE TABLE server_users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    server_pk BIGINT UNSIGNED NOT NULL,
    user_pk BIGINT UNSIGNED NOT NULL,

    uuid CHAR(36) NOT NULL,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    UNIQUE KEY uq_server_users_server_user (
        server_pk,
        user_pk
    ),

    UNIQUE KEY uq_server_users_server_uuid (
        server_pk,
        uuid
    ),

    KEY idx_server_users_user (
        user_pk,
        enabled
    ),

    CONSTRAINT fk_server_users_server
        FOREIGN KEY (server_pk)
        REFERENCES servers(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_server_users_user
        FOREIGN KEY (user_pk)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;
