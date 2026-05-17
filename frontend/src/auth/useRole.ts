import { useCallback, useEffect, useMemo, useState } from "react";

import {
  canCreate,
  canDelete,
  canEdit,
  canUpdateQuantity,
  DEFAULT_ROLE,
  isUserRole,
  ROLE_STORAGE_KEY,
} from "./roles";
import type { UserRole } from "./roles";

const ROLE_CHANGE_EVENT = "detail-warehouse-role-change";

function readStoredRole(): UserRole {
  if (typeof window === "undefined") {
    return DEFAULT_ROLE;
  }

  const storedRole = window.localStorage.getItem(ROLE_STORAGE_KEY);
  return isUserRole(storedRole) ? storedRole : DEFAULT_ROLE;
}

export function useRole() {
  const [role, setRoleState] = useState<UserRole>(readStoredRole);

  const setRole = useCallback((nextRole: UserRole) => {
    window.localStorage.setItem(ROLE_STORAGE_KEY, nextRole);
    setRoleState(nextRole);
    window.dispatchEvent(
      new CustomEvent<UserRole>(ROLE_CHANGE_EVENT, { detail: nextRole }),
    );
  }, []);

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key === ROLE_STORAGE_KEY) {
        setRoleState(readStoredRole());
      }
    };

    const handleRoleChange = (event: Event) => {
      const roleChangeEvent = event as CustomEvent<UserRole>;

      if (isUserRole(roleChangeEvent.detail)) {
        setRoleState(roleChangeEvent.detail);
      }
    };

    window.addEventListener("storage", handleStorage);
    window.addEventListener(ROLE_CHANGE_EVENT, handleRoleChange);

    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener(ROLE_CHANGE_EVENT, handleRoleChange);
    };
  }, []);

  return useMemo(
    () => ({
      role,
      setRole,
      canCreate: canCreate(role),
      canEdit: canEdit(role),
      canDelete: canDelete(role),
      canUpdateQuantity: canUpdateQuantity(role),
    }),
    [role, setRole],
  );
}
