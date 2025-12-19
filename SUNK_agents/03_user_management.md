# User Management

> **Source**: [Manage cluster access](https://docs.coreweave.com/docs/products/sunk/manage_sunk/control_cluster_access), [SUNK User Provisioning](https://docs.coreweave.com/docs/products/sunk/manage_sunk/control_cluster_access/provision_users_in_sunk), [Manage users with a directory service](https://docs.coreweave.com/docs/products/sunk/manage_sunk/control_cluster_access/manage_users_with_a_directory_service), [nsscache](https://docs.coreweave.com/docs/products/sunk/manage_sunk/control_cluster_access/nsscache)

SUNK integrates heavily with enterprise identity systems to ensure seamless access control. The primary mechanism is **SUNK User Provisioning (SUP)**.

## SUNK User Provisioning (SUP)

SUP is a controller that synchronizes user identity information from an external source (IdP) into the SUNK cluster.

### Capabilities
- **User Sync**: Creates POSIX users and groups on all login and compute nodes.
- **Slurm Account Sync**: Creates corresponding Slurm Accounts and Associations.
- **SSH Key Management**: Distributes public keys to authorized users' `~/.ssh/authorized_keys`.

### nsscache Integration

From SUNK v6.6+, SUP typically uses `nsscache` to distribute user/group databases (passwd/group files) efficiently to all nodes.
-   **Mechanism**: SUP fetches users from IdP -> Generates SQLite DB -> Distributes via HTTP/S3 to nodes.
-   **Benefit**: Faster than direct LDAP lookups on every node, especially for large clusters.

## Identity Providers

SUP supports:
- **SCIM**: For direct integration with Okta, Microsoft Entra ID (Azure AD), Google Workspace.
- **LDAP**: For integration with OpenLDAP or Active Directory.
- **CoreWeave IAM**: Can sync users defined in the CoreWeave Cloud portal.

### Configuration Concepts

In the Helm chart, you configure the "Directory Service" source.

```yaml
# Conceptual configuration
directoryService:
  type: "scim" # or "ldap"
  scim:
    endpoint: "https://api.coreweave.com/scim/v2"
    tokenSecret: "my-scim-secret"
  # or
  ldap:
    uri: "ldaps://ldap.example.com"
    bindDn: "cn=admin,dc=example,dc=com"
    userBaseDn: "ou=users,dc=example,dc=com"
```

## SSH Access

- **Login Nodes**: Exposed via a LoadBalancer Service (usually TCP port 22, mapped to a public IP).
- **Authentication**: Public Key Authentication is the standard. Password auth is typically disabled for security.
- **Home Directories**:
    - Users land in `/home/<username>`.
    - This directory is a shared mount (NFS/Weka/Ceph), persisting data across sessions and making it available on compute nodes.

## Role Based Access Control (RBAC)

- **Slurm Accounts**: Used to track usage and enforce limits (QOS).
- **Admins**: Users can be designated as Slurm operators or admins via specific groups synced from the IdP (e.g., `slurm-admins` group).

