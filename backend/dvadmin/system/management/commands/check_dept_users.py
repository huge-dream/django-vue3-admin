# -*- coding: utf-8 -*-
"""
排查 Dept 层级数据及 Users 关联
用法: python manage.py check_dept_users
"""
from django.core.management.base import BaseCommand
from django.db import connection
class Command(BaseCommand):
    help = "排查 Dept 表层级数据、Users 重复及部门 parent 关联"

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("1. 检查 Users 表是否有重复 id")
        self.stdout.write("=" * 60)
        self._check_duplicate_users()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("2. 检查 Dept 表是否有重复 id")
        self.stdout.write("=" * 60)
        self._check_duplicate_depts()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("3. 检查 Dept parent 关联（parent_id 指向不存在的部门）")
        self.stdout.write("=" * 60)
        self._check_dept_parent_orphans()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("4. 检查 Dept 层级循环（parent 链成环）")
        self.stdout.write("=" * 60)
        self._check_dept_cycles()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("5. 用户及其部门 parent 链（前 20 条）")
        self.stdout.write("=" * 60)
        self._show_users_dept_chain()

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("6. Dept 全表 id/parent_id/name（便于人工核对）")
        self.stdout.write("=" * 60)
        self._show_all_depts()

    def _run_sql(self, sql, params=None):
        with connection.cursor() as c:
            c.execute(sql, params or [])
            columns = [col[0] for col in c.description]
            return [dict(zip(columns, row)) for row in c.fetchall()]

    def _get_table(self, name):
        from django.conf import settings
        prefix = getattr(settings, "TABLE_PREFIX", "")
        return f"{prefix}{name}"

    def _check_duplicate_users(self):
        t = self._get_table("system_users")
        # 重复 id
        rows = self._run_sql(
            f"SELECT id, COUNT(*) as cnt FROM {t} GROUP BY id HAVING COUNT(*) > 1"
        )
        if rows:
            self.stdout.write(self.style.ERROR(f"  [!!] 发现重复 Users.id: {rows}"))
            for r in rows:
                detail = self._run_sql(f"SELECT id, username, name, dept_id FROM {t} WHERE id = %s", [r["id"]])
                self.stdout.write(f"      详情: {detail}")
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] Users 表无重复 id"))
        # 重复 username（JWT 若按 username 查会触发 MultipleObjectsReturned）
        dup_user = self._run_sql(
            f"SELECT username, COUNT(*) as cnt FROM {t} GROUP BY username HAVING COUNT(*) > 1"
        )
        if dup_user:
            self.stdout.write(self.style.ERROR(f"  [!!] 发现重复 username: {dup_user}"))
        else:
            self.stdout.write(self.style.SUCCESS("  [OK] Users 表无重复 username"))

    def _check_duplicate_depts(self):
        t = self._get_table("system_dept")
        rows = self._run_sql(
            f"SELECT id, COUNT(*) as cnt FROM {t} GROUP BY id HAVING COUNT(*) > 1"
        )
        if not rows:
            self.stdout.write(self.style.SUCCESS("  [OK] Dept 表无重复 id"))
            return
        self.stdout.write(self.style.ERROR(f"  [!!] 发现重复 Dept.id: {rows}"))

    def _check_dept_parent_orphans(self):
        t = self._get_table("system_dept")
        # parent_id 非空且指向不存在的 id
        rows = self._run_sql(f"""
            SELECT d.id, d.name, d.parent_id
            FROM {t} d
            LEFT JOIN {t} p ON d.parent_id = p.id
            WHERE d.parent_id IS NOT NULL AND p.id IS NULL
        """)
        if not rows:
            self.stdout.write(self.style.SUCCESS("  [OK] 无 parent 指向不存在的部门"))
            return
        self.stdout.write(self.style.ERROR(f"  [!!] 以下部门 parent_id 指向不存在的 id:"))
        for r in rows:
            self.stdout.write(f"      id={r['id']} name={r['name']} parent_id={r['parent_id']}")

    def _check_dept_cycles(self):
        t = self._get_table("system_dept")
        rows = self._run_sql(f"SELECT id, parent_id, name FROM {t} ORDER BY id")
        dept_map = {r["id"]: r for r in rows}
        cycles = []
        for d in rows:
            seen = set()
            cur = d
            while cur and cur["parent_id"]:
                if cur["id"] in seen:
                    cycles.append((d["id"], d["name"], list(seen)))
                    break
                seen.add(cur["id"])
                cur = dept_map.get(cur["parent_id"])
        if not cycles:
            self.stdout.write(self.style.SUCCESS("  [OK] 未发现 parent 链成环"))
            return
        self.stdout.write(self.style.ERROR(f"  [!!] 发现循环: {cycles}"))

    def _show_users_dept_chain(self):
        """用 raw SQL 避免 ORM 触发 MultipleObjectsReturned"""
        ut = self._get_table("system_users")
        dt = self._get_table("system_dept")
        users = self._run_sql(
            f"SELECT id, username, name, dept_id FROM {ut} ORDER BY id LIMIT 20"
        )
        depts = {r["id"]: r for r in self._run_sql(f"SELECT id, parent_id, name FROM {dt}")}
        for u in users:
            dept_id = u.get("dept_id")
            if not dept_id:
                self.stdout.write(f"  user id={u['id']} username={u['username']} dept=None")
                continue
            chain = []
            cur_id = dept_id
            visited = set()
            while cur_id:
                if cur_id in visited:
                    chain.append(f"[循环!id={cur_id}]")
                    break
                d = depts.get(cur_id)
                if not d:
                    chain.append(f"[不存在id={cur_id}]")
                    break
                visited.add(cur_id)
                chain.append(f"{d['name']}(id={d['id']})")
                cur_id = d.get("parent_id")
            self.stdout.write(f"  user id={u['id']} username={u['username']} dept_chain: {' -> '.join(chain)}")

    def _show_all_depts(self):
        t = self._get_table("system_dept")
        rows = self._run_sql(f"SELECT id, parent_id, name FROM {t} ORDER BY id")
        self.stdout.write("  id | parent_id | name")
        self.stdout.write("  " + "-" * 50)
        for r in rows:
            self.stdout.write(f"  {r['id']} | {r['parent_id']} | {r['name']}")
