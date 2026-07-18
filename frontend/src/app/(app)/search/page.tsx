"use client";

import * as React from "react";
import Link from "next/link";
import { Search as SearchIcon, Sparkles, Type } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useSearch } from "@/hooks/use-dashboard";
import type { SearchResultItem } from "@/types";

function ResultList({ items }: { items: SearchResultItem[] }) {
  if (items.length === 0) {
    return <p className="py-6 text-center text-sm text-muted-foreground">No results</p>;
  }
  return (
    <div className="space-y-2">
      {items.map((item) => {
        const href = item.course_id
          ? item.type === "lesson"
            ? `/courses/${item.course_id}/lessons/${item.id}`
            : `/courses/${item.course_id}`
          : `/courses/${item.id}`;
        return (
          <Link key={`${item.type}-${item.id}`} href={href}>
            <div className="rounded-lg border p-3 transition-colors hover:bg-accent">
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium">{item.title}</p>
                <Badge variant="outline" className="capitalize">
                  {item.type}
                </Badge>
              </div>
              {item.snippet && (
                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{item.snippet}</p>
              )}
            </div>
          </Link>
        );
      })}
    </div>
  );
}

export default function SearchPage() {
  const [query, setQuery] = React.useState("");
  const [debounced, setDebounced] = React.useState("");

  React.useEffect(() => {
    const timer = setTimeout(() => setDebounced(query), 350);
    return () => clearTimeout(timer);
  }, [query]);

  const { data, isFetching } = useSearch(debounced);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Search</h1>
        <p className="text-muted-foreground">Find lessons, chapters and topics across your courses.</p>
      </div>

      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          autoFocus
          placeholder="Search keywords or concepts…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-9"
        />
      </div>

      {debounced.trim().length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Start typing to search your learning content.
          </CardContent>
        </Card>
      ) : isFetching ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Type className="h-4 w-4 text-primary" /> Keyword matches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResultList items={data?.keyword_results ?? []} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Sparkles className="h-4 w-4 text-primary" /> Semantic matches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResultList items={data?.semantic_results ?? []} />
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
