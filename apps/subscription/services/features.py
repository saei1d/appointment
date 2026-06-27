def active_subscription(provider):
    from django.utils import timezone
    return provider.subscriptions.select_related('plan').filter(
        is_active=True,
        start_date__lte=timezone.localdate(),
        end_date__gte=timezone.localdate(),
    ).first()


def provider_has_feature(provider, feature_code):
    subscription = active_subscription(provider)
    if not subscription:
        return False
    return bool(getattr(subscription.plan, feature_code, False))
