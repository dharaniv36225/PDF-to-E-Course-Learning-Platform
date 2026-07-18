"use client";

import Link from "next/link";
import { LogOut, Settings, User as UserIcon } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Avatar } from "@/components/ui/avatar";
import { Dropdown, DropdownItem } from "@/components/ui/dropdown";
import { useLogout } from "@/hooks/use-auth";
import { useAuthStore } from "@/store/auth-store";
import { initials } from "@/lib/utils";

export function Navbar() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center justify-between border-b bg-background/80 px-4 backdrop-blur md:px-8">
      <div className="md:hidden text-lg font-bold gradient-text">LearnPDF</div>
      <div className="flex-1" />
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <Dropdown
          trigger={
            <button className="flex items-center gap-2 rounded-full">
              <Avatar src={user?.avatar_url} fallback={initials(user?.full_name, user?.email)} />
            </button>
          }
        >
          <div className="px-3 py-2 border-b">
            <p className="text-sm font-medium truncate">{user?.full_name ?? "Learner"}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
          </div>
          <Link href="/profile">
            <DropdownItem>
              <UserIcon className="h-4 w-4" /> Profile
            </DropdownItem>
          </Link>
          <Link href="/profile">
            <DropdownItem>
              <Settings className="h-4 w-4" /> Settings
            </DropdownItem>
          </Link>
          <DropdownItem className="text-destructive" onClick={logout}>
            <LogOut className="h-4 w-4" /> Sign out
          </DropdownItem>
        </Dropdown>
      </div>
    </header>
  );
}
