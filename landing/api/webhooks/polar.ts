// Polar webhook receiver (PO 권고 패턴·M25 시도 로그)
// Polar SDK validateEvent·Edge Runtime·Request/Response Web API
import { validateEvent, WebhookVerificationError } from "@polar-sh/sdk/webhooks";

export const config = { runtime: "nodejs" };

export async function POST(req: Request) {
  const body = await req.text();
  const headers = Object.fromEntries(req.headers);

  // [POLAR_ATTEMPT] 무조건 로그 (M25·외부 시도 = 진짜 데이터)
  const ts = new Date().toISOString();
  console.log(
    `[POLAR_ATTEMPT] ${ts} ip=${headers["x-forwarded-for"] || "?"} body=${body.slice(0, 200)}`
  );

  try {
    const event: any = validateEvent(
      body,
      headers,
      process.env.POLAR_WEBHOOK_SECRET as string
    );

    // 매출 milestone (order.created·order.paid·subscription.active)
    if (
      event?.type === "order.created" ||
      event?.type === "order.paid" ||
      event?.type === "subscription.active"
    ) {
      const data = event.data || {};
      console.log(
        JSON.stringify({
          milestone: "revenue",
          ts,
          type: event.type,
          amount: data.amount ?? data.net_amount ?? "?",
          currency: data.currency ?? "?",
          customerEmail: data.customer?.email ?? "?",
        })
      );
    } else {
      console.log(`[POLAR_EVENT] ${ts} type=${event?.type || "?"}`);
    }

    return Response.json({ received: true, type: event?.type });
  } catch (err) {
    if (err instanceof WebhookVerificationError) {
      console.log(`[POLAR_VALIDATION_FAIL] ${ts} reason=signature_mismatch`);
      return new Response("Invalid signature", { status: 403 });
    }
    console.log(`[POLAR_VALIDATION_FAIL] ${ts} reason=${(err as Error).message}`);
    throw err;
  }
}

export async function GET() {
  return Response.json({ ok: true, service: "polar-webhook-receiver", pattern: "PO" });
}
