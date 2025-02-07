import secrets
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from irrigation.models import WaterUsage, DataCollection, FlowRate, Configuration, ConfigFertil, TimeFerti

def apresentation_view(request):
    return render(request, 'comum/apresentation.html')

@login_required
def configuration_view(request):
    # Get or create instances with correct field names
    flow_rate_instance, _ = FlowRate.objects.get_or_create(
        id=1, 
        defaults={'rate': 0.0}
    )
    configuration_instance, _ = Configuration.objects.get_or_create(
        id=1, 
        defaults={'token': ''}
    )
    config_fertil_instance, _ = ConfigFertil.objects.get_or_create(
        id=1, 
        defaults={'duration_hours': 1}  # Changed from time_fertil to duration_hours
    )
    time_ferti_instance, _ = TimeFerti.objects.get_or_create(
        id=1, 
        defaults={'duration_ms': 0}  # Changed from time_ferti_ms to duration_ms
    )

    if request.method == 'POST':
        # Update flow rate
        if 'update_flow_rate' in request.POST:
            new_rate = request.POST.get('flow_rate')
            if new_rate:
                try:
                    flow_rate_instance.rate = float(new_rate)
                    flow_rate_instance.save()
                except ValueError:
                    print("Invalid flow rate value provided.")

        # Update fertilization cycle duration
        if 'time_fertil' in request.POST:
            new_duration = request.POST.get('time_fertil')
            try:
                config_fertil_instance.duration_hours = int(new_duration)
                config_fertil_instance.save()
            except ValueError:
                print("Invalid duration value provided.")

        # Update fertilization pump duration
        if 'update_time_fertil' in request.POST:
            new_duration_ms = request.POST.get('time_ferti_ms')
            if new_duration_ms:
                try:
                    time_ferti_instance.duration_ms = int(new_duration_ms)
                    time_ferti_instance.save()
                except ValueError:
                    print("Invalid duration_ms value provided.")

        # Generate new token
        if 'generate_token' in request.POST:
            new_token = secrets.token_hex(16)
            configuration_instance.token = new_token
            configuration_instance.save()

        return redirect('configuration')

    return render(request, 'comum/configuration.html', {
        'flow_rate': flow_rate_instance,
        'configuracao': configuration_instance,
        'config_fertil': config_fertil_instance,
        'time_ferti': time_ferti_instance,
    })
