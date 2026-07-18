import * as React from "react";
import { cn } from "@/lib/utils";

interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string | null;
  fallback: string;
}

function Avatar({ src, fallback, className, ...props }: AvatarProps) {
  return (
    <div
      className={cn(
        "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full bg-primary/15 text-primary items-center justify-center text-sm font-semibold",
        className
      )}
      {...props}
    >
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={fallback} className="h-full w-full object-cover" />
      ) : (
        <span>{fallback}</span>
      )}
    </div>
  );
}

export { Avatar };
