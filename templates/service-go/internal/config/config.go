// Package config reads service configuration from environment variables.
package config

import (
	"log/slog"
	"os"
	"strings"
)

// Config holds runtime configuration.
type Config struct {
	Port     string
	LogLevel slog.Level
}

// Load reads PORT and LOG_LEVEL (DEBUG, INFO, WARN, ERROR) from the environment.
func Load() Config {
	return Config{
		Port:     getenv("PORT", "8080"),
		LogLevel: parseLevel(getenv("LOG_LEVEL", "INFO")),
	}
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func parseLevel(s string) slog.Level {
	var l slog.Level
	if err := l.UnmarshalText([]byte(strings.ToUpper(s))); err != nil {
		return slog.LevelInfo
	}
	return l
}
