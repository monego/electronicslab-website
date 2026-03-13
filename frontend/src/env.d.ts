import type { Temporal as _Temporal } from '@js-temporal/polyfill';

declare global {
  const Temporal: typeof _Temporal;
  namespace Temporal {
    type ZonedDateTime = _Temporal.ZonedDateTime;
    type Instant = _Temporal.Instant;
    type PlainDate = _Temporal.PlainDate;
    type PlainDateTime = _Temporal.PlainDateTime;
    type PlainTime = _Temporal.PlainTime;
    type Duration = _Temporal.Duration;
  }
}

declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: string;
    VUE_ROUTER_MODE: 'hash' | 'history' | 'abstract' | undefined;
    VUE_ROUTER_BASE: string | undefined;
  }
}