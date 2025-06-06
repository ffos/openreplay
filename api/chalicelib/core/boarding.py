from chalicelib.core import projects
from chalicelib.core import users
from chalicelib.core.log_tools import datadog, stackdriver, sentry
from chalicelib.core.modules import TENANT_CONDITION
from chalicelib.utils import pg_client


def get_state(tenant_id):
    pids = projects.get_projects_ids(tenant_id=tenant_id)
    with pg_client.PostgresClient() as cur:
        recorded = False
        meta = False

        if len(pids) > 0:
            cur.execute(
                cur.mogrify(
                    """SELECT EXISTS((  SELECT 1
                                                FROM public.sessions AS s
                                                WHERE s.project_id IN %(ids)s)) AS exists;""",
                    {"ids": tuple(pids)},
                )
            )
            recorded = cur.fetchone()["exists"]
            meta = False
            if recorded:
                query = cur.mogrify(
                    f"""SELECT EXISTS((SELECT 1
                               FROM public.projects AS p
                                        LEFT JOIN LATERAL ( SELECT 1
                                                            FROM public.sessions
                                                            WHERE sessions.project_id = p.project_id
                                                              AND sessions.user_id IS NOT NULL
                                                            LIMIT 1) AS sessions(user_id) ON (TRUE)
                               WHERE {TENANT_CONDITION} AND p.deleted_at ISNULL
                                 AND ( sessions.user_id IS NOT NULL OR p.metadata_1 IS NOT NULL
                                       OR p.metadata_2 IS NOT NULL OR p.metadata_3 IS NOT NULL
                                       OR p.metadata_4 IS NOT NULL OR p.metadata_5 IS NOT NULL
                                       OR p.metadata_6 IS NOT NULL OR p.metadata_7 IS NOT NULL
                                       OR p.metadata_8 IS NOT NULL OR p.metadata_9 IS NOT NULL
                                       OR p.metadata_10 IS NOT NULL )
                                   )) AS exists;""",
                    {"tenant_id": tenant_id},
                )
                cur.execute(query)

                meta = cur.fetchone()["exists"]

    return [
        {
            "task": "Install OpenReplay",
            "done": recorded,
            "URL": "https://docs.openreplay.com/getting-started/quick-start",
        },
        {
            "task": "Identify Users",
            "done": meta,
            "URL": "https://docs.openreplay.com/data-privacy-security/metadata",
        },
        {
            "task": "Invite Team Members",
            "done": len(users.get_members(tenant_id=tenant_id)) > 1,
            "URL": "https://app.openreplay.com/client/manage-users",
        },
        {
            "task": "Integrations",
            "done": len(datadog.get_all(tenant_id=tenant_id)) > 0
            or len(sentry.get_all(tenant_id=tenant_id)) > 0
            or len(stackdriver.get_all(tenant_id=tenant_id)) > 0,
            "URL": "https://docs.openreplay.com/integrations",
        },
    ]


def get_state_installing(tenant_id):
    pids = projects.get_projects_ids(tenant_id=tenant_id)
    with pg_client.PostgresClient() as cur:
        recorded = False

        if len(pids) > 0:
            cur.execute(
                cur.mogrify(
                    """SELECT EXISTS((  SELECT 1
                                                FROM public.sessions AS s
                                                WHERE s.project_id IN %(ids)s)) AS exists;""",
                    {"ids": tuple(pids)},
                )
            )
            recorded = cur.fetchone()["exists"]

    return {
        "task": "Install OpenReplay",
        "done": recorded,
        "URL": "https://docs.openreplay.com/getting-started/quick-start",
    }


def get_state_identify_users(tenant_id):
    with pg_client.PostgresClient() as cur:
        query = cur.mogrify(
            f"""SELECT EXISTS((SELECT 1
                                       FROM public.projects AS p
                                                LEFT JOIN LATERAL ( SELECT 1
                                                                    FROM public.sessions
                                                                    WHERE sessions.project_id = p.project_id
                                                                      AND sessions.user_id IS NOT NULL
                                                                    LIMIT 1) AS sessions(user_id) ON (TRUE)
                                       WHERE {TENANT_CONDITION} AND p.deleted_at ISNULL
                                         AND ( sessions.user_id IS NOT NULL OR p.metadata_1 IS NOT NULL
                                               OR p.metadata_2 IS NOT NULL OR p.metadata_3 IS NOT NULL
                                               OR p.metadata_4 IS NOT NULL OR p.metadata_5 IS NOT NULL
                                               OR p.metadata_6 IS NOT NULL OR p.metadata_7 IS NOT NULL
                                               OR p.metadata_8 IS NOT NULL OR p.metadata_9 IS NOT NULL
                                               OR p.metadata_10 IS NOT NULL )
                                           )) AS exists;""",
            {"tenant_id": tenant_id},
        )
        cur.execute(query)

        meta = cur.fetchone()["exists"]

    return {
        "task": "Identify Users",
        "done": meta,
        "URL": "https://docs.openreplay.com/data-privacy-security/metadata",
    }


def get_state_manage_users(tenant_id):
    return {
        "task": "Invite Team Members",
        "done": len(users.get_members(tenant_id=tenant_id)) > 1,
        "URL": "https://app.openreplay.com/client/manage-users",
    }


def get_state_integrations(tenant_id):
    return {
        "task": "Integrations",
        "done": len(datadog.get_all(tenant_id=tenant_id)) > 0
        or len(sentry.get_all(tenant_id=tenant_id)) > 0
        or len(stackdriver.get_all(tenant_id=tenant_id)) > 0,
        "URL": "https://docs.openreplay.com/integrations",
    }
