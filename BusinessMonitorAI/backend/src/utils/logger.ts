import { createLogger, format, transports, Logger as WinstonLogger } from 'winston';
import { config } from 'dotenv';

config();

const { combine, timestamp, printf } = format;

const logFormat = printf(({ level, message, timestamp }: { level: string; message: string; timestamp: string }) => {
  return `${timestamp} [${level.toUpperCase()}]: ${message}`;
});

export class Logger {
  private static instance: Logger;
  private logger: WinstonLogger;

  private constructor() {
    this.logger = createLogger({
      format: combine(
        timestamp(),
        logFormat
      ),
      transports: [
        new transports.Console({
          level: process.env.NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new transports.File({
          filename: 'error.log',
          level: 'error'
        }),
        new transports.File({
          filename: 'combined.log'
        })
      ]
    });
  }

  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  public debug(message: string, ...meta: any[]): void {
    this.logger.debug(message, ...meta);
  }

  public info(message: string, ...meta: any[]): void {
    this.logger.info(message, ...meta);
  }

  public warn(message: string, ...meta: any[]): void {
    this.logger.warn(message, ...meta);
  }

  public error(message: string, ...meta: any[]): void {
    this.logger.error(message, ...meta);
  }
}
