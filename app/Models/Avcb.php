<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Avcb extends Model
{
    use HasFactory;

    protected $fillable = [
        'license_id',
        'project_id',
        'ppci_number',
        'issued_at',
        'expires_at',
        'has_compensatory_measures',
        'status',
        'metadata',
    ];

    protected $casts = [
        'metadata' => 'array',
        'issued_at' => 'date',
        'expires_at' => 'date',
        'has_compensatory_measures' => 'boolean',
    ];

    public function project()
    {
        return $this->belongsTo(Project::class);
    }

    public function license()
    {
        return $this->belongsTo(License::class);
    }

    public function attachments()
    {
        return $this->morphMany(Attachment::class, 'attachable');
    }
}
