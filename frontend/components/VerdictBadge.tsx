import { Badge } from "@/components/ui";

export function VerdictBadge({ passed }: { passed: boolean }) {
  return (
    <Badge tone={passed ? "success" : "danger"}>{passed ? "PASS" : "REGRESSION"}</Badge>
  );
}
