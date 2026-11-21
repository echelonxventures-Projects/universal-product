package relay

import (
	"context"

	"github.com/twmb/franz-go/pkg/kgo"
)

// Kafka publishes to a Kafka-API bus (ADR-012). Produce is synchronous so a row is marked published only after
// the broker acknowledged it (acks=all, idempotent producer).
type Kafka struct{ Client *kgo.Client }

func NewKafka(brokers []string) (*Kafka, error) {
	c, err := kgo.NewClient(kgo.SeedBrokers(brokers...), kgo.RequiredAcks(kgo.AllISRAcks()), kgo.AllowAutoTopicCreation())
	if err != nil {
		return nil, err
	}
	return &Kafka{Client: c}, nil
}

func (k *Kafka) Publish(ctx context.Context, topic, key string, value []byte) error {
	return k.Client.ProduceSync(ctx, &kgo.Record{Topic: topic, Key: []byte(key), Value: value,
		Headers: []kgo.RecordHeader{{Key: "content-type", Value: []byte("application/cloudevents+json")}}}).FirstErr()
}

func (k *Kafka) Close() { k.Client.Close() }
