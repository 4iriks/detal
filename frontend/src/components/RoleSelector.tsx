import { useRole } from "../auth/useRole";
import { USER_ROLES } from "../auth/roles";
import type { UserRole } from "../auth/roles";

export default function RoleSelector() {
  const { role, setRole } = useRole();

  return (
    <label className="role-selector">
      <span>Роль</span>
      <select
        value={role}
        onChange={(event) => setRole(event.target.value as UserRole)}
      >
        {USER_ROLES.map((availableRole) => (
          <option key={availableRole} value={availableRole}>
            {availableRole}
          </option>
        ))}
      </select>
    </label>
  );
}
